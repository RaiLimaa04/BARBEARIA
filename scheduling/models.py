from django.db import models
from django.core.validators import RegexValidator
from core.models import Service, Cliente


class Appointment(models.Model):
    # Relação com o cliente (opcional para manter compatibilidade)
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        verbose_name='Cliente',
        null=True, 
        blank=True,
        related_name='appointments'
    )
    
    # Campos existentes para compatibilidade
    client_name = models.CharField(max_length=100, verbose_name='Nome do Cliente')
    client_phone = models.CharField(
        max_length=15,
        verbose_name='Telefone',
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\)\s\d{4,5}-\d{4}$',
                message='Formato: (11) 99999-9999'
            )
        ]
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Serviço')
    date = models.DateField(verbose_name='Data')
    time = models.TimeField(verbose_name='Horário')
    is_confirmed = models.BooleanField(default=False, verbose_name='Confirmado')
    is_cancelled = models.BooleanField(default=False, verbose_name='Cancelado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    notes = models.TextField(blank=True, verbose_name='Observações')

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-date', '-time']
        unique_together = ['date', 'time']

    def __str__(self):
        if self.cliente:
            return f"{self.cliente.user.get_full_name()} - {self.service.name} - {self.date} {self.time}"
        else:
            return f"{self.client_name} - {self.service.name} - {self.date} {self.time}"

    @property
    def status(self):
        if self.is_cancelled:
            return 'Cancelado'
        elif self.is_confirmed:
            return 'Confirmado'
        else:
            return 'Pendente'
    
    def save(self, *args, **kwargs):
        # Se há um cliente associado, usar seus dados
        if self.cliente:
            self.client_name = self.cliente.user.get_full_name() or self.cliente.user.username
            self.client_phone = self.cliente.telefone
        super().save(*args, **kwargs) 