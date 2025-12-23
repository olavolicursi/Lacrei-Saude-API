from django.db import models
from professionals.models import Professional

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('AGENDADA', 'Agendada'),
        ('CONFIRMADA', 'Confirmada'),
        ('REALIZADA', 'Realizada'),
        ('CANCELADA', 'Cancelada'),
    ]

    professional = models.ForeignKey(
        Professional,
        on_delete=models.PROTECT,
        related_name='appointments'
    )
    data_hora = models.DateTimeField()
    duracao_minutos = models.PositiveIntegerField(default=60)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AGENDADA'
    )

    # Paciente (simplificado)
    paciente_nome = models.CharField(max_length=200)
    paciente_email = models.EmailField()
    paciente_telefone = models.CharField(max_length=15)

    observacoes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['professional', 'data_hora']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duracao_minutos__gte=15),
                name='duracao_minima_15min'
            )
        ]

    def __str__(self):
        return f"Consulta com {self.professional.nome_social} em {self.data_hora.strftime('%Y-%m-%d %H:%M')} - {self.paciente_nome}"