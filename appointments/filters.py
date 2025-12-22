from django_filters import rest_framework as filters
from .models import Appointment


class AppointmentFilter(filters.FilterSet):
    """Filtros avançados para consultas"""
    
    # Filtros de data
    data_inicio = filters.DateTimeFilter(
        field_name='data_hora',
        lookup_expr='gte'
    )
    data_fim = filters.DateTimeFilter(
        field_name='data_hora',
        lookup_expr='lte'
    )
    
    # Filtro por mês/ano
    mes = filters.NumberFilter(
        field_name='data_hora__month'
    )
    ano = filters.NumberFilter(
        field_name='data_hora__year'
    )
    
    # Filtros de status múltiplos
    status_in = filters.MultipleChoiceFilter(
        field_name='status',
        choices=Appointment.STATUS_CHOICES
    )
    
    # Filtro por profissional
    professional_name = filters.CharFilter(
        field_name='professional__nome_social',
        lookup_expr='icontains'
    )
    
    # Filtro por paciente
    paciente_nome = filters.CharFilter(
        lookup_expr='icontains'
    )
    
    class Meta:
        model = Appointment
        fields = {
            'professional': ['exact'],
            'status': ['exact'],
            'data_hora': ['exact', 'gte', 'lte'],
        }
