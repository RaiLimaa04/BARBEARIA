from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Gera todos os dados de teste para o sistema da barbearia'

    def add_arguments(self, parser):
        parser.add_argument(
            '--setup-only',
            action='store_true',
            help='Executa apenas a configuração inicial (serviços, clientes, horários)'
        )
        parser.add_argument(
            '--appointments-only',
            action='store_true',
            help='Executa apenas a geração de agendamentos (futuros e passados)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de dias para agendamentos futuros (padrão: 30)'
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=90,
            help='Número de dias para trás para histórico (padrão: 90)'
        )
        parser.add_argument(
            '--appointments-per-day',
            type=int,
            default=5,
            help='Número de agendamentos por dia (padrão: 5)'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando geração completa de dados de teste...')
        
        if options['appointments_only']:
            self.stdout.write('📅 Gerando apenas agendamentos...')
            self._generate_appointments(options)
        elif options['setup_only']:
            self.stdout.write('⚙️  Configurando apenas dados básicos...')
            self._setup_basic_data()
        else:
            self.stdout.write('🔄 Executando geração completa de dados...')
            self._setup_basic_data()
            self._generate_appointments(options)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Geração de dados concluída com sucesso!')
        )
        
        # Mostrar resumo final
        self._show_final_summary()

    def _setup_basic_data(self):
        """Configura dados básicos (serviços, clientes, horários)"""
        self.stdout.write('\n📋 Configurando dados básicos...')
        try:
            call_command('setup_test_data')
            self.stdout.write('✅ Dados básicos configurados com sucesso!')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao configurar dados básicos: {e}')
            )

    def _generate_appointments(self, options):
        """Gera agendamentos futuros e passados"""
        self.stdout.write('\n📅 Gerando agendamentos passados (histórico)...')
        try:
            call_command(
                'generate_past_appointments',
                days_back=options['days_back'],
                appointments_per_day=options['appointments_per_day'] // 2  # Menos agendamentos no histórico
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao gerar agendamentos passados: {e}')
            )
        
        self.stdout.write('\n📅 Gerando agendamentos futuros...')
        try:
            call_command(
                'generate_test_appointments',
                days=options['days'],
                appointments_per_day=options['appointments_per_day']
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao gerar agendamentos futuros: {e}')
            )

    def _show_final_summary(self):
        """Mostra resumo final dos dados gerados"""
        from core.models import Service, Cliente, BusinessHour
        from scheduling.models import Appointment
        from django.db.models import Count
        
        self.stdout.write('\n📊 === RESUMO FINAL ===')
        
        # Contadores básicos
        services_count = Service.objects.count()
        clients_count = Cliente.objects.count()
        business_hours_count = BusinessHour.objects.count()
        appointments_count = Appointment.objects.count()
        
        self.stdout.write(f'📋 Serviços: {services_count}')
        self.stdout.write(f'👥 Clientes: {clients_count}')
        self.stdout.write(f'🕐 Horários de funcionamento: {business_hours_count}')
        self.stdout.write(f'📅 Agendamentos: {appointments_count}')
        
        # Estatísticas de agendamentos
        if appointments_count > 0:
            confirmed = Appointment.objects.filter(is_confirmed=True).count()
            cancelled = Appointment.objects.filter(is_cancelled=True).count()
            pending = Appointment.objects.filter(is_confirmed=False, is_cancelled=False).count()
            
            self.stdout.write(f'✅ Confirmados: {confirmed}')
            self.stdout.write(f'❌ Cancelados: {cancelled}')
            self.stdout.write(f'⏳ Pendentes: {pending}')
        
        # Próximos agendamentos
        from django.utils import timezone
        upcoming = Appointment.objects.filter(
            date__gte=timezone.now().date(),
            is_cancelled=False
        ).order_by('date', 'time')[:5]
        
        if upcoming.exists():
            self.stdout.write('\n📅 Próximos agendamentos:')
            for appointment in upcoming:
                status = '✅' if appointment.is_confirmed else '⏳'
                self.stdout.write(
                    f'  {status} {appointment.date.strftime("%d/%m")} '
                    f'{appointment.time.strftime("%H:%M")} - {appointment.client_name}'
                )
        
        self.stdout.write('\n🎉 Sistema pronto para testes!')
        self.stdout.write('💡 Dica: Use o admin do Django para visualizar todos os dados.') 