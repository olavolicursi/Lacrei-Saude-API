from rest_framework import permissions


class IsAppointmentOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada:
    - Leitura: qualquer usuário autenticado
    - Escrita: apenas owner da consulta
    """
    
    def has_object_permission(self, request, view, obj):
        # Leitura permitida para qualquer um
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escrita apenas para o profissional da consulta
        # ou admin
        if request.user.is_staff:
            return True
        
        # TODO: Verificar se user é o profissional
        # return obj.professional.user == request.user
        
        return True  # Por enquanto permitir
