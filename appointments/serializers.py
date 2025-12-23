from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Appointment
from professionals.serializers import ProfessionalSerializer
from core.validators import sanitize_html, validate_no_sql_injection


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer completo para consultas"""
    
    professional_details = ProfessionalSerializer(
        source='professional',
        read_only=True
    )
    
    # Campos calculados
    duracao_horas = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    is_past = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'professional',
            'professional_details',
            'data_hora',
            'duracao_minutos',
            'duracao_horas',
            'status',
            'status_display',
            'paciente_nome',
            'paciente_email',
            'paciente_telefone',
            'observacoes',
            'is_past',
            'can_cancel',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_duracao_horas(self, obj):
        """Retorna duração em formato legível"""
        hours = obj.duracao_minutos // 60
        minutes = obj.duracao_minutos % 60
        if hours > 0:
            return f"{hours}h{minutes:02d}min" if minutes else f"{hours}h"
        return f"{minutes}min"
    
    def get_is_past(self, obj):
        """Verifica se a consulta já passou"""
        return obj.data_hora < timezone.now()
    
    def get_can_cancel(self, obj):
        """Verifica se pode cancelar (até 24h antes)"""
        if obj.status in ['CANCELADA', 'REALIZADA']:
            return False
        time_until = obj.data_hora - timezone.now()
        return time_until > timedelta(hours=24)
    
    def validate_data_hora(self, value):
        """Valida se a data/hora é futura"""
        if value < timezone.now():
            raise serializers.ValidationError(
                "Não é possível agendar consulta no passado"
            )
        
        # Validar horário comercial (8h às 18h)
        if value.hour < 8 or value.hour >= 18:
            raise serializers.ValidationError(
                "Horário deve ser entre 8h e 18h"
            )
        
        # Validar dias úteis (segunda a sexta)
        if value.weekday() >= 5:  # 5=sábado, 6=domingo
            raise serializers.ValidationError(
                "Consultas apenas em dias úteis"
            )
        
        return value
    
    def validate_duracao_minutos(self, value):
        """Valida duração da consulta"""
        if value < 15:
            raise serializers.ValidationError(
                "Duração mínima de 15 minutos"
            )
        if value > 240:  # 4 horas
            raise serializers.ValidationError(
                "Duração máxima de 4 horas"
            )
        # Validar múltiplos de 15
        if value % 15 != 0:
            raise serializers.ValidationError(
                "Duração deve ser múltiplo de 15 minutos"
            )
        return value
    
    def validate_paciente_nome(self, value):
        """Sanitiza e valida nome do paciente"""
        validate_no_sql_injection(value)
        return sanitize_html(value)
    
    def validate_paciente_email(self, value):
        """Valida email do paciente"""
        validate_no_sql_injection(value)
        return value.lower()
    
    def validate_paciente_telefone(self, value):
        """Valida e formata telefone"""
        import re
        validate_no_sql_injection(value)
        clean = re.sub(r'\D', '', value)
        if len(clean) < 10 or len(clean) > 11:
            raise serializers.ValidationError(
                "Telefone inválido. Use formato: (11) 99999-9999"
            )
        return value
    
    def validate_observacoes(self, value):
        """Sanitiza observações"""
        if value:
            validate_no_sql_injection(value)
            return sanitize_html(value)
        return value
    
    def validate(self, data):
        """Validações complexas"""
        # Verificar conflito de horário
        professional = data.get('professional')
        data_hora = data.get('data_hora')
        duracao = data.get('duracao_minutos', 60)
        
        if professional and data_hora:
            # Calcular fim da consulta
            fim_consulta = data_hora + timedelta(minutes=duracao)
            
            # Buscar consultas conflitantes
            conflicting = Appointment.objects.filter(
                professional=professional,
                data_hora__lt=fim_consulta,
                data_hora__gte=data_hora - timedelta(minutes=duracao),
                status__in=['AGENDADA', 'CONFIRMADA']
            )
            
            # Excluir a própria consulta se for update
            if self.instance:
                conflicting = conflicting.exclude(pk=self.instance.pk)
            
            if conflicting.exists():
                raise serializers.ValidationError(
                    "Profissional já possui consulta neste horário"
                )
        
        return data


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para criação"""
    
    class Meta:
        model = Appointment
        fields = [
            'professional',
            'data_hora',
            'duracao_minutos',
            'paciente_nome',
            'paciente_email',
            'paciente_telefone',
            'observacoes',
        ]
    
    def validate(self, data):
        # Reutilizar validações do serializer principal
        serializer = AppointmentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return data


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização (campos limitados)"""
    
    class Meta:
        model = Appointment
        fields = [
            'data_hora',
            'duracao_minutos',
            'status',
            'observacoes',
        ]
    
    def validate_status(self, value):
        """Validar transições de status"""
        if not self.instance:
            return value
        
        current_status = self.instance.status
        
        # Regras de transição
        valid_transitions = {
            'AGENDADA': ['CONFIRMADA', 'CANCELADA'],
            'CONFIRMADA': ['REALIZADA', 'CANCELADA'],
            'REALIZADA': [],  # Status final
            'CANCELADA': [],  # Status final
        }
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Transição de {current_status} para {value} não permitida"
            )
        
        return value


class AppointmentListSerializer(serializers.ModelSerializer):
    """Serializer otimizado para listagens"""
    
    professional_name = serializers.CharField(
        source='professional.nome_social',
        read_only=True
    )
    professional_profession = serializers.CharField(
        source='professional.get_profissao_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'professional',
            'professional_name',
            'professional_profession',
            'data_hora',
            'duracao_minutos',
            'status',
            'status_display',
            'paciente_nome',
        ]


class AppointmentCancelSerializer(serializers.Serializer):
    """Serializer para cancelamento"""
    
    motivo = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )
    
    def validate(self, data):
        appointment = self.context.get('appointment')
        
        if not appointment:
            raise serializers.ValidationError("Consulta não encontrada")
        
        if appointment.status in ['CANCELADA', 'REALIZADA']:
            raise serializers.ValidationError(
                f"Consulta já está {appointment.get_status_display()}"
            )
        
        # Verificar prazo de 24h
        time_until = appointment.data_hora - timezone.now()
        if time_until < timedelta(hours=24):
            raise serializers.ValidationError(
                "Não é possível cancelar com menos de 24h de antecedência"
            )
        
        return data
