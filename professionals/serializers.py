from rest_framework import serializers
from .models import Professional
from core.validators import sanitize_html, validate_no_sql_injection

class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_nome_social(self, value):
        """Sanitiza e valida nome social"""
        validate_no_sql_injection(value)
        return sanitize_html(value)
    
    def validate_logradouro(self, value):
        """Sanitiza logradouro"""
        validate_no_sql_injection(value)
        return sanitize_html(value)
    
    def validate_complemento(self, value):
        """Sanitiza complemento"""
        if value:
            validate_no_sql_injection(value)
            return sanitize_html(value)
        return value
    
    def validate_bairro(self, value):
        """Sanitiza bairro"""
        validate_no_sql_injection(value)
        return sanitize_html(value)
    
    def validate_cidade(self, value):
        """Sanitiza cidade"""
        validate_no_sql_injection(value)
        return sanitize_html(value)

    def validate_email(self, value):
        # Validação customizada
        validate_no_sql_injection(value)
        return value.lower()

    def validate_telefone(self, value):
        # Remover caracteres especiais e validar
        import re
        validate_no_sql_injection(value)
        clean = re.sub(r'\D', '', value)
        if len(clean) < 10:
            raise serializers.ValidationError("Telefone inválido")
        return value