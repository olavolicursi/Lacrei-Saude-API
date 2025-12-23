from django.db import models
from django.core.validators import RegexValidator

class Professional(models.Model):
    PROFESSION_CHOICES = [
        ('MEDICO', 'Médico'),
        ('PSICOLOGO', 'Psicólogo'),
        ('NUTRICIONISTA', 'Nutricionista'),
        # ... outros
    ]

    nome_social = models.CharField(max_length=200)
    profissao = models.CharField(max_length=50, choices=PROFESSION_CHOICES)
    registro_profissional = models.CharField(max_length=50, unique=True)

    # Endereço
    cep = models.CharField(max_length=9)
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)

    # Contato
    telefone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    # Metadados
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome_social']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['registro_profissional']),
        ]
    
    def __str__(self):
        return f"{self.nome_social} - {self.get_profissao_display()} ({self.registro_profissional})"