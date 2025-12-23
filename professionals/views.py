from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Professional
from .serializers import ProfessionalSerializer

class ProfessionalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar profissionais de saúde.
    
    Endpoints disponíveis:
    - GET /api/v1/professionals/ - Lista todos os profissionais ativos
    - POST /api/v1/professionals/ - Cria um novo profissional
    - GET /api/v1/professionals/{id}/ - Retorna um profissional específico
    - PUT /api/v1/professionals/{id}/ - Atualiza um profissional
    - PATCH /api/v1/professionals/{id}/ - Atualiza parcialmente um profissional
    - DELETE /api/v1/professionals/{id}/ - Desativa um profissional (soft delete)
    """
    queryset = Professional.objects.filter(ativo=True)
    serializer_class = ProfessionalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['profissao', 'cidade', 'estado']
    search_fields = ['nome_social', 'email', 'registro_profissional']
    ordering_fields = ['nome_social', 'profissao', 'created_at']
    ordering = ['nome_social']
    
    def perform_destroy(self, instance):
        """Soft delete: marca como inativo ao invés de deletar"""
        instance.ativo = False
        instance.save()
    
    @action(detail=False, methods=['get'])
    def inativos(self, request):
        """Retorna profissionais inativos"""
        queryset = Professional.objects.filter(ativo=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reativar(self, request, pk=None):
        """Reativa um profissional inativo"""
        professional = self.get_object()
        professional.ativo = True
        professional.save()
        serializer = self.get_serializer(professional)
        return Response(serializer.data)