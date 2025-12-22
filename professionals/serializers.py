from rest_framework import serializers
from .models import Professional

class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_email(self, value):
        # Validação customizada
        return value.lower()

    def validate_telefone(self, value):
        # Remover caracteres especiais e validar
        import re
        clean = re.sub(r'\D', '', value)
        if len(clean) < 10:
            raise serializers.ValidationError("Telefone inválido")
        return value