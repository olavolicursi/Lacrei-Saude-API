from django.contrib import admin
from .models import Professional

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('nome_social', 'profissao', 'registro_profissional', 'email', 'cidade', 'estado', 'ativo')
    list_filter = ('profissao', 'estado', 'ativo')
    search_fields = ('nome_social', 'email', 'registro_profissional')
    list_editable = ('ativo',)
    ordering = ('nome_social',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome_social', 'profissao', 'registro_profissional')
        }),
        ('Endereço', {
            'fields': ('cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )
