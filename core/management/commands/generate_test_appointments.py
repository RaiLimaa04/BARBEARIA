from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
import random
from decimal import Decimal
from core.models import Service, Cliente, BusinessHour
from scheduling.models import Appointment
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Gera dados fictícios de agendamentos para testar o sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de dias para gerar agendamentos (padrão: 30)'
        )
        parser.add_argument(
            '--appointments-per-day',
            type=int,
            default=5,
            help='Número de agendamentos por dia (padrão: 5)'
        )

    def handle(self, *args, **options):
        days = options['days']
        appointments_per_day = options['appointments_per_day']
        
        self.stdout.write('Gerando dados fictícios de agendamentos...')
        
        # Verificar se existem serviços
        services = Service.objects.all()
        if not services.exists():
            self.stdout.write(
                self.style.ERROR('Nenhum serviço encontrado. Crie alguns serviços primeiro.')
            )
            return
        
        # Verificar se existem clientes
        clientes = Cliente.objects.all()
        if not clientes.exists():
            self.stdout.write(
                self.style.ERROR('Nenhum cliente encontrado. Crie alguns clientes primeiro.')
            )
            return
        
        # Verificar horários de funcionamento
        business_hours = BusinessHour.objects.filter(is_active=True)
        if not business_hours.exists():
            self.stdout.write(
                self.style.ERROR('Nenhum horário de funcionamento encontrado. Configure os horários primeiro.')
            )
            return
        
        # Gerar agendamentos
        appointments_created = 0
        start_date = timezone.now().date()
        
        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Pular domingos (dia 6)
            if current_date.weekday() == 6:
                continue
            
            # Encontrar horário de funcionamento para este dia
            day_business_hours = business_hours.filter(day_of_week=current_date.weekday()).first()
            if not day_business_hours:
                continue
            
            # Gerar horários disponíveis
            available_times = self._generate_available_times(
                day_business_hours.start_time,
                day_business_hours.end_time
            )
            
            # Gerar agendamentos para este dia
            for _ in range(appointments_per_day):
                if not available_times:
                    break
                
                # Escolher horário aleatório
                appointment_time = random.choice(available_times)
                available_times.remove(appointment_time)
                
                # Escolher cliente e serviço aleatórios
                cliente = random.choice(clientes)
                service = random.choice(services)
                
                # Criar agendamento
                appointment = Appointment.objects.create(
                    cliente=cliente,
                    client_name=cliente.user.get_full_name() or cliente.user.username,
                    client_phone=cliente.telefone,
                    service=service,
                    date=current_date,
                    time=appointment_time,
                    is_confirmed=random.choice([True, True, True, False]),  # 75% confirmados
                    is_cancelled=random.choice([False, False, False, False, True]),  # 20% cancelados
                    notes=random.choice([
                        '',
                        'Cliente solicitou horário específico',
                        'Primeira vez no estabelecimento',
                        'Cliente fiel',
                        'Preferência por barbeiro específico',
                        'Alergia a produtos específicos',
                        'Horário de almoço',
                        'Trazer criança junto'
                    ])
                )
                
                appointments_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Sucesso! {appointments_created} agendamentos foram criados para os próximos {days} dias.'
            )
        )
        
        # Mostrar estatísticas
        self._show_statistics()
    
    def _generate_available_times(self, start_time, end_time):
        """Gera lista de horários disponíveis entre start_time e end_time"""
        times = []
        current_time = start_time
        
        while current_time < end_time:
            times.append(current_time)
            # Adicionar 30 minutos
            current_time = (
                datetime.combine(datetime.min, current_time) + 
                timedelta(minutes=30)
            ).time()
        
        return times
    
    def _show_statistics(self):
        """Mostra estatísticas dos agendamentos criados"""
        total_appointments = Appointment.objects.count()
        confirmed_appointments = Appointment.objects.filter(is_confirmed=True).count()
        cancelled_appointments = Appointment.objects.filter(is_cancelled=True).count()
        pending_appointments = Appointment.objects.filter(
            is_confirmed=False, 
            is_cancelled=False
        ).count()
        
        self.stdout.write('\n=== ESTATÍSTICAS ===')
        self.stdout.write(f'Total de agendamentos: {total_appointments}')
        self.stdout.write(f'Agendamentos confirmados: {confirmed_appointments}')
        self.stdout.write(f'Agendamentos cancelados: {cancelled_appointments}')
        self.stdout.write(f'Agendamentos pendentes: {pending_appointments}')
        
        # Estatísticas por serviço
        self.stdout.write('\n=== AGENDAMENTOS POR SERVIÇO ===')
        for service in Service.objects.all():
            count = Appointment.objects.filter(service=service).count()
            self.stdout.write(f'{service.name}: {count}')
        
        # Próximos agendamentos
        self.stdout.write('\n=== PRÓXIMOS AGENDAMENTOS ===')
        upcoming = Appointment.objects.filter(
            date__gte=timezone.now().date(),
            is_cancelled=False
        ).order_by('date', 'time')[:10]
        
        for appointment in upcoming:
            status = '✅' if appointment.is_confirmed else '⏳'
            self.stdout.write(
                f'{status} {appointment.date.strftime("%d/%m/%Y")} '
                f'{appointment.time.strftime("%H:%M")} - '
                f'{appointment.client_name} - {appointment.service.name}'
            ) 