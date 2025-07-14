from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
import random
from core.models import Service, Cliente, BusinessHour
from scheduling.models import Appointment


class Command(BaseCommand):
    help = 'Gera agendamentos passados (histórico) para dados mais realistas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-back',
            type=int,
            default=90,
            help='Número de dias para trás para gerar histórico (padrão: 90)'
        )
        parser.add_argument(
            '--appointments-per-day',
            type=int,
            default=3,
            help='Número de agendamentos por dia no histórico (padrão: 3)'
        )

    def handle(self, *args, **options):
        days_back = options['days_back']
        appointments_per_day = options['appointments_per_day']
        
        self.stdout.write('Gerando agendamentos passados (histórico)...')
        
        # Verificar se existem dados necessários
        services = Service.objects.all()
        clientes = Cliente.objects.all()
        business_hours = BusinessHour.objects.filter(is_active=True)
        
        if not services.exists() or not clientes.exists() or not business_hours.exists():
            self.stdout.write(
                self.style.ERROR('Dados insuficientes. Execute setup_test_data primeiro.')
            )
            return
        
        # Gerar agendamentos passados
        appointments_created = 0
        end_date = timezone.now().date() - timedelta(days=1)  # Ontem
        start_date = end_date - timedelta(days=days_back)
        
        current_date = start_date
        while current_date <= end_date:
            # Pular domingos
            if current_date.weekday() == 6:
                current_date += timedelta(days=1)
                continue
            
            # Encontrar horário de funcionamento para este dia
            day_business_hours = business_hours.filter(day_of_week=current_date.weekday()).first()
            if not day_business_hours:
                current_date += timedelta(days=1)
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
                
                # Para agendamentos passados, a maioria deve estar confirmada
                is_confirmed = random.choice([True, True, True, True, False])  # 80% confirmados
                is_cancelled = random.choice([False, False, False, False, False, True])  # 16% cancelados
                
                # Criar agendamento
                appointment = Appointment.objects.create(
                    cliente=cliente,
                    client_name=cliente.user.get_full_name() or cliente.user.username,
                    client_phone=cliente.telefone,
                    service=service,
                    date=current_date,
                    time=appointment_time,
                    is_confirmed=is_confirmed,
                    is_cancelled=is_cancelled,
                    notes=random.choice([
                        '',
                        'Cliente satisfeito com o serviço',
                        'Retorno de cliente fiel',
                        'Primeira visita do cliente',
                        'Cliente recomendou o estabelecimento',
                        'Serviço realizado com sucesso',
                        'Cliente solicitou ajustes',
                        'Horário de pico - muito movimento'
                    ])
                )
                
                appointments_created += 1
            
            current_date += timedelta(days=1)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Sucesso! {appointments_created} agendamentos passados foram criados '
                f'para os últimos {days_back} dias.'
            )
        )
        
        # Mostrar estatísticas do histórico
        self._show_history_statistics()
    
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
    
    def _show_history_statistics(self):
        """Mostra estatísticas dos agendamentos passados"""
        past_date = timezone.now().date() - timedelta(days=1)
        
        past_appointments = Appointment.objects.filter(date__lt=timezone.now().date())
        total_past = past_appointments.count()
        completed_past = past_appointments.filter(is_confirmed=True, is_cancelled=False).count()
        cancelled_past = past_appointments.filter(is_cancelled=True).count()
        
        self.stdout.write('\n=== ESTATÍSTICAS DO HISTÓRICO ===')
        self.stdout.write(f'Total de agendamentos passados: {total_past}')
        self.stdout.write(f'Agendamentos realizados: {completed_past}')
        self.stdout.write(f'Agendamentos cancelados: {cancelled_past}')
        
        if total_past > 0:
            completion_rate = (completed_past / total_past) * 100
            self.stdout.write(f'Taxa de realização: {completion_rate:.1f}%')
        
        # Serviços mais populares no histórico
        self.stdout.write('\n=== SERVIÇOS MAIS POPULARES (HISTÓRICO) ===')
        from django.db.models import Count
        popular_services = past_appointments.values('service__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        for service in popular_services:
            self.stdout.write(f'{service["service__name"]}: {service["count"]} agendamentos')
        
        # Clientes mais frequentes
        self.stdout.write('\n=== CLIENTES MAIS FREQUENTES (HISTÓRICO) ===')
        frequent_clients = past_appointments.values('client_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        for client in frequent_clients:
            self.stdout.write(f'{client["client_name"]}: {client["count"]} visitas') 