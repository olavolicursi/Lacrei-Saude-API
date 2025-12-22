from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta, datetime, time
from django.db.models import Q
import logging

from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentUpdateSerializer,
    AppointmentListSerializer,
    AppointmentCancelSerializer,
)
from .filters import AppointmentFilter
from .permissions import IsAppointmentOwnerOrReadOnly

logger = logging.getLogger(__name__)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gerenciamento de consultas
    
    list: Listar todas as consultas
    create: Criar nova consulta
    retrieve: Detalhar consulta específica
    update: Atualizar consulta
    partial_update: Atualizar parcialmente
    destroy: Deletar consulta
    
    Ações customizadas:
    - upcoming: Consultas futuras
    - past: Consultas passadas
    - by_professional: Consultas por profissional
    - cancel: Cancelar consulta
    - confirm: Confirmar consulta
    - complete: Marcar como realizada
    - statistics: Estatísticas
    - available_slots: Horários disponíveis
    """
    
    queryset = Appointment.objects.select_related('professional').all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AppointmentFilter
    search_fields = ['paciente_nome', 'paciente_email', 'professional__nome_social']
    ordering_fields = ['data_hora', 'created_at', 'status']
    ordering = ['-data_hora']
    
    def get_queryset(self):
        """Otimizar queries com select_related"""
        queryset = Appointment.objects.select_related(
            'professional'
        ).all()
        
        # Filtrar por profissional se especificado
        professional_id = self.request.query_params.get('professional_id')
        if professional_id:
            queryset = queryset.filter(professional_id=professional_id)
        
        # Filtrar por status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtrar por período
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(data_hora__gte=start_date)
        if end_date:
            queryset = queryset.filter(data_hora__lte=end_date)
        
        return queryset
    
    def get_serializer_class(self):
        """Retornar serializer apropriado por ação"""
        if self.action == 'list':
            return AppointmentListSerializer
        elif self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AppointmentUpdateSerializer
        elif self.action == 'cancel':
            return AppointmentCancelSerializer
        return AppointmentSerializer
    
    def perform_create(self, serializer):
        """Criar consulta e fazer logging"""
        appointment = serializer.save()
        logger.info(
            f"Consulta criada: ID={appointment.id}, "
            f"Profissional={appointment.professional.nome_social}, "
            f"Data={appointment.data_hora}"
        )
        
        # TODO: Enviar email de confirmação
        # send_appointment_confirmation_email(appointment)
    
    def perform_update(self, serializer):
        """Atualizar e fazer logging"""
        old_instance = self.get_object()
        appointment = serializer.save()
        
        logger.info(
            f"Consulta atualizada: ID={appointment.id}, "
            f"Status: {old_instance.status} -> {appointment.status}"
        )
        
        # TODO: Enviar notificação de alteração
        # if old_instance.data_hora != appointment.data_hora:
        #     send_appointment_change_email(appointment)
    
    def perform_destroy(self, instance):
        """Soft delete - apenas marcar como cancelada"""
        instance.status = 'CANCELADA'
        instance.observacoes += f"\n[Deletada em {timezone.now()}]"
        instance.save()
        
        logger.warning(f"Consulta deletada: ID={instance.id}")
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Retornar consultas futuras"""
        appointments = self.get_queryset().filter(
            data_hora__gte=timezone.now(),
            status__in=['AGENDADA', 'CONFIRMADA']
        ).order_by('data_hora')
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def past(self, request):
        """Retornar consultas passadas"""
        appointments = self.get_queryset().filter(
            Q(data_hora__lt=timezone.now()) |
            Q(status__in=['REALIZADA', 'CANCELADA'])
        ).order_by('-data_hora')
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-professional/(?P<professional_id>[0-9]+)')
    def by_professional(self, request, professional_id=None):
        """
        Retornar consultas de um profissional específico
        
        GET /api/v1/appointments/by-professional/123/
        GET /api/v1/appointments/by-professional/123/?status=AGENDADA
        """
        appointments = self.get_queryset().filter(
            professional_id=professional_id
        )
        
        # Aplicar filtros adicionais
        status_filter = request.query_params.get('status')
        if status_filter:
            appointments = appointments.filter(status=status_filter)
        
        page = self.paginate_queryset(appointments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancelar uma consulta
        
        POST /api/v1/appointments/123/cancel/
        {
            "motivo": "Motivo do cancelamento"
        }
        """
        appointment = self.get_object()
        
        serializer = AppointmentCancelSerializer(
            data=request.data,
            context={'appointment': appointment}
        )
        serializer.is_valid(raise_exception=True)
        
        # Cancelar
        appointment.status = 'CANCELADA'
        motivo = serializer.validated_data.get('motivo', '')
        if motivo:
            appointment.observacoes += f"\n[Cancelamento] {motivo}"
        appointment.save()
        
        logger.info(f"Consulta cancelada: ID={appointment.id}")
        
        # TODO: Enviar notificação
        # send_appointment_cancellation_email(appointment)
        
        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirmar uma consulta
        
        POST /api/v1/appointments/123/confirm/
        """
        appointment = self.get_object()
        
        if appointment.status != 'AGENDADA':
            return Response(
                {'error': 'Apenas consultas agendadas podem ser confirmadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'CONFIRMADA'
        appointment.save()
        
        logger.info(f"Consulta confirmada: ID={appointment.id}")
        
        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Marcar consulta como realizada
        
        POST /api/v1/appointments/123/complete/
        """
        appointment = self.get_object()
        
        if appointment.status not in ['AGENDADA', 'CONFIRMADA']:
            return Response(
                {'error': 'Status inválido para conclusão'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se já passou da data
        if appointment.data_hora > timezone.now():
            return Response(
                {'error': 'Consulta ainda não ocorreu'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'REALIZADA'
        appointment.save()
        
        logger.info(f"Consulta concluída: ID={appointment.id}")
        
        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Estatísticas de consultas
        
        GET /api/v1/appointments/statistics/
        GET /api/v1/appointments/statistics/?professional_id=123
        """
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'by_status': {
                'agendadas': queryset.filter(status='AGENDADA').count(),
                'confirmadas': queryset.filter(status='CONFIRMADA').count(),
                'realizadas': queryset.filter(status='REALIZADA').count(),
                'canceladas': queryset.filter(status='CANCELADA').count(),
            },
            'upcoming': queryset.filter(
                data_hora__gte=timezone.now(),
                status__in=['AGENDADA', 'CONFIRMADA']
            ).count(),
            'past_7_days': queryset.filter(
                data_hora__gte=timezone.now() - timedelta(days=7),
                data_hora__lte=timezone.now()
            ).count(),
            'next_7_days': queryset.filter(
                data_hora__gte=timezone.now(),
                data_hora__lte=timezone.now() + timedelta(days=7)
            ).count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """
        Retornar horários disponíveis para um profissional
        
        GET /api/v1/appointments/available-slots/?professional_id=123&date=2024-01-15
        """
        professional_id = request.query_params.get('professional_id')
        date_str = request.query_params.get('date')
        
        if not professional_id or not date_str:
            return Response(
                {'error': 'professional_id e date são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar consultas já agendadas neste dia
        existing_appointments = Appointment.objects.filter(
            professional_id=professional_id,
            data_hora__date=target_date,
            status__in=['AGENDADA', 'CONFIRMADA']
        ).values_list('data_hora', 'duracao_minutos')
        
        # Gerar slots disponíveis (8h às 18h, intervalos de 30min)
        slots = []
        current_time = datetime.combine(target_date, time(8, 0))
        end_time = datetime.combine(target_date, time(18, 0))
        
        while current_time < end_time:
            # Verificar se slot está livre
            is_available = True
            for appt_time, duration in existing_appointments:
                appt_end = appt_time + timedelta(minutes=duration)
                slot_end = current_time + timedelta(minutes=30)
                
                # Verificar sobreposição
                if (current_time < appt_end and slot_end > appt_time):
                    is_available = False
                    break
            
            slots.append({
                'time': current_time.strftime('%H:%M'),
                'available': is_available
            })
            
            current_time += timedelta(minutes=30)
        
        return Response({
            'date': date_str,
            'professional_id': professional_id,
            'slots': slots
        })
