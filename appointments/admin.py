from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'paciente_nome',
        'professional_link',
        'data_hora_formatted',
        'duracao_display',
        'status_badge',
        'created_at'
    )
    list_filter = (
        'status',
        'professional__profissao',
        'data_hora',
        'created_at'
    )
    search_fields = (
        'paciente_nome',
        'paciente_email',
        'paciente_telefone',
        'professional__nome_social',
        'observacoes'
    )
    date_hierarchy = 'data_hora'
    ordering = ('-data_hora',)
    
    readonly_fields = ('created_at', 'updated_at', 'appointment_details')
    
    fieldsets = (
        ('Profissional', {
            'fields': ('professional',)
        }),
        ('Data e Horário', {
            'fields': ('data_hora', 'duracao_minutos')
        }),
        ('Informações do Paciente', {
            'fields': ('paciente_nome', 'paciente_email', 'paciente_telefone')
        }),
        ('Status e Observações', {
            'fields': ('status', 'observacoes')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'appointment_details'),
            'classes': ('collapse',)
        }),
    )
    
    def professional_link(self, obj):
        """Link para o profissional"""
        from django.urls import reverse
        from django.utils.html import format_html
        
        url = reverse('admin:professionals_professional_change', args=[obj.professional.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.professional.nome_social
        )
    professional_link.short_description = 'Profissional'
    
    def data_hora_formatted(self, obj):
        """Formata data/hora de forma legível"""
        now = timezone.now()
        if obj.data_hora < now:
            color = '#999'
            icon = '✓'
        elif obj.data_hora < now + timezone.timedelta(days=1):
            color = '#f00'
            icon = '⚠'
        else:
            color = '#000'
            icon = '📅'
        
        return format_html(
            '<span style="color: {};">{} {}</span>',
            color,
            icon,
            obj.data_hora.strftime('%d/%m/%Y %H:%M')
        )
    data_hora_formatted.short_description = 'Data/Hora'
    data_hora_formatted.admin_order_field = 'data_hora'
    
    def duracao_display(self, obj):
        """Exibe duração formatada"""
        hours = obj.duracao_minutos // 60
        minutes = obj.duracao_minutos % 60
        
        if hours > 0:
            return f"{hours}h{minutes:02d}min" if minutes else f"{hours}h"
        return f"{minutes}min"
    duracao_display.short_description = 'Duração'
    
    def status_badge(self, obj):
        """Badge colorido para status"""
        colors = {
            'AGENDADA': '#17a2b8',
            'CONFIRMADA': '#28a745',
            'REALIZADA': '#6c757d',
            'CANCELADA': '#dc3545',
        }
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#000'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def appointment_details(self, obj):
        """Detalhes completos da consulta"""
        # Verificar se o objeto já foi salvo
        if not obj.pk or not obj.data_hora:
            return format_html('<p>{}</p>', 'Salve a consulta para ver os detalhes completos.')
        
        fim_consulta = obj.data_hora + timezone.timedelta(minutes=obj.duracao_minutos)
        
        html = f"""
        <div style="line-height: 1.8;">
            <p><strong>ID:</strong> {obj.id}</p>
            <p><strong>Profissional:</strong> {obj.professional.nome_social} 
               ({obj.professional.get_profissao_display()})</p>
            <p><strong>Registro:</strong> {obj.professional.registro_profissional}</p>
            <p><strong>Email Profissional:</strong> {obj.professional.email}</p>
            <hr>
            <p><strong>Paciente:</strong> {obj.paciente_nome}</p>
            <p><strong>Email:</strong> {obj.paciente_email}</p>
            <p><strong>Telefone:</strong> {obj.paciente_telefone}</p>
            <hr>
            <p><strong>Início:</strong> {obj.data_hora.strftime('%d/%m/%Y às %H:%M')}</p>
            <p><strong>Término:</strong> {fim_consulta.strftime('%d/%m/%Y às %H:%M')}</p>
            <p><strong>Duração:</strong> {self.duracao_display(obj)}</p>
            <p><strong>Status:</strong> {obj.get_status_display()}</p>
            <hr>
            <p><strong>Criado em:</strong> {obj.created_at.strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p><strong>Última atualização:</strong> {obj.updated_at.strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        """
        return format_html(html)
    appointment_details.short_description = 'Detalhes Completos'
    
    def get_queryset(self, request):
        """Otimizar query com select_related"""
        return super().get_queryset(request).select_related('professional')
    
    actions = ['marcar_como_confirmada', 'marcar_como_realizada', 'cancelar_consultas']
    
    def marcar_como_confirmada(self, request, queryset):
        """Action para confirmar múltiplas consultas"""
        updated = queryset.filter(status='AGENDADA').update(status='CONFIRMADA')
        self.message_user(
            request,
            f'{updated} consulta(s) confirmada(s) com sucesso.'
        )
    marcar_como_confirmada.short_description = 'Confirmar consultas selecionadas'
    
    def marcar_como_realizada(self, request, queryset):
        """Action para marcar como realizadas"""
        updated = queryset.filter(
            status__in=['AGENDADA', 'CONFIRMADA']
        ).update(status='REALIZADA')
        self.message_user(
            request,
            f'{updated} consulta(s) marcada(s) como realizada(s).'
        )
    marcar_como_realizada.short_description = 'Marcar como realizadas'
    
    def cancelar_consultas(self, request, queryset):
        """Action para cancelar consultas"""
        updated = queryset.exclude(
            status__in=['REALIZADA', 'CANCELADA']
        ).update(status='CANCELADA')
        self.message_user(
            request,
            f'{updated} consulta(s) cancelada(s).'
        )
    cancelar_consultas.short_description = 'Cancelar consultas selecionadas'
