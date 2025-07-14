from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome do Serviço')
    description = models.TextField(verbose_name='Descrição')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço')
    duration = models.IntegerField(verbose_name='Duração (minutos)')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['name']

    def __str__(self):
        return self.name


class BusinessHour(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name='Dia da Semana')
    start_time = models.TimeField(verbose_name='Horário de Início')
    end_time = models.TimeField(verbose_name='Horário de Fim')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Horário de Funcionamento'
        verbose_name_plural = 'Horários de Funcionamento'
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.start_time} às {self.end_time}"


class BarbershopInfo(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nome da Barbearia')
    description = models.TextField(verbose_name='Descrição')
    phone = models.CharField(max_length=20, verbose_name='Telefone')
    whatsapp = models.CharField(max_length=20, verbose_name='WhatsApp')
    address = models.TextField(verbose_name='Endereço')
    instagram = models.CharField(max_length=100, blank=True, verbose_name='Instagram')
    facebook = models.CharField(max_length=100, blank=True, verbose_name='Facebook')
    logo = models.ImageField(upload_to='barbershop/', blank=True, verbose_name='Logo')

    class Meta:
        verbose_name = 'Informações da Barbearia'
        verbose_name_plural = 'Informações da Barbearia'

    def __str__(self):
        return self.name


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    data_nascimento = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    endereco = models.TextField(blank=True, verbose_name='Endereço')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


@receiver(post_save, sender=User)
def create_cliente_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'cliente'):
        Cliente.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_cliente_profile(sender, instance, **kwargs):
    if hasattr(instance, 'cliente'):
        instance.cliente.save()