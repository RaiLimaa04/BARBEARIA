from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Service, Cliente, BusinessHour
from datetime import time


class Command(BaseCommand):
    help = 'Configura dados de teste completos para o sistema da barbearia'

    def handle(self, *args, **options):
        self.stdout.write('Configurando dados de teste...')
        
        # Criar serviços
        self._create_services()
        
        # Criar clientes
        self._create_clients()
        
        # Criar horários de funcionamento
        self._create_business_hours()
        
        self.stdout.write(
            self.style.SUCCESS('Dados de teste configurados com sucesso!')
        )

    def _create_services(self):
        """Cria serviços fictícios"""
        services_data = [
            {
                'name': 'Corte Masculino',
                'description': 'Corte tradicional masculino com acabamento perfeito',
                'price': 35.00,
                'duration': 30
            },
            {
                'name': 'Barba',
                'description': 'Acabamento de barba com navalha e produtos premium',
                'price': 25.00,
                'duration': 20
            },
            {
                'name': 'Corte + Barba',
                'description': 'Corte masculino completo com acabamento de barba',
                'price': 50.00,
                'duration': 45
            },
            {
                'name': 'Corte Infantil',
                'description': 'Corte especializado para crianças até 12 anos',
                'price': 25.00,
                'duration': 25
            },
            {
                'name': 'Hidratação',
                'description': 'Tratamento hidratante para cabelo e couro cabeludo',
                'price': 40.00,
                'duration': 30
            },
            {
                'name': 'Pigmentação',
                'description': 'Coloração e pigmentação de cabelo e barba',
                'price': 60.00,
                'duration': 60
            },
            {
                'name': 'Sobrancelha',
                'description': 'Design e modelagem de sobrancelhas',
                'price': 15.00,
                'duration': 15
            },
            {
                'name': 'Pacote Completo',
                'description': 'Corte + Barba + Hidratação + Sobrancelha',
                'price': 90.00,
                'duration': 90
            }
        ]
        
        for service_data in services_data:
            # Verificar se já existe um serviço com este nome
            existing_services = Service.objects.filter(name=service_data['name'])
            if existing_services.exists():
                self.stdout.write(f'ℹ️  Serviço já existe: {service_data["name"]}')
                continue
            
            # Criar novo serviço
            service = Service.objects.create(**service_data)
            self.stdout.write(f'✅ Serviço criado: {service.name}')

    def _create_clients(self):
        """Cria clientes fictícios"""
        clients_data = [
            {
                'username': 'joao.silva',
                'first_name': 'João',
                'last_name': 'Silva',
                'email': 'joao.silva@email.com',
                'telefone': '(11) 99999-1111'
            },
            {
                'username': 'pedro.santos',
                'first_name': 'Pedro',
                'last_name': 'Santos',
                'email': 'pedro.santos@email.com',
                'telefone': '(11) 99999-2222'
            },
            {
                'username': 'carlos.oliveira',
                'first_name': 'Carlos',
                'last_name': 'Oliveira',
                'email': 'carlos.oliveira@email.com',
                'telefone': '(11) 99999-3333'
            },
            {
                'username': 'marcos.rodrigues',
                'first_name': 'Marcos',
                'last_name': 'Rodrigues',
                'email': 'marcos.rodrigues@email.com',
                'telefone': '(11) 99999-4444'
            },
            {
                'username': 'lucas.ferreira',
                'first_name': 'Lucas',
                'last_name': 'Ferreira',
                'email': 'lucas.ferreira@email.com',
                'telefone': '(11) 99999-5555'
            },
            {
                'username': 'andre.costa',
                'first_name': 'André',
                'last_name': 'Costa',
                'email': 'andre.costa@email.com',
                'telefone': '(11) 99999-6666'
            },
            {
                'username': 'rafael.lima',
                'first_name': 'Rafael',
                'last_name': 'Lima',
                'email': 'rafael.lima@email.com',
                'telefone': '(11) 99999-7777'
            },
            {
                'username': 'gabriel.martins',
                'first_name': 'Gabriel',
                'last_name': 'Martins',
                'email': 'gabriel.martins@email.com',
                'telefone': '(11) 99999-8888'
            },
            {
                'username': 'thiago.almeida',
                'first_name': 'Thiago',
                'last_name': 'Almeida',
                'email': 'thiago.almeida@email.com',
                'telefone': '(11) 99999-9999'
            },
            {
                'username': 'bruno.souza',
                'first_name': 'Bruno',
                'last_name': 'Souza',
                'email': 'bruno.souza@email.com',
                'telefone': '(11) 88888-1111'
            }
        ]
        
        for client_data in clients_data:
            user, created = User.objects.get_or_create(
                username=client_data['username'],
                defaults={
                    'first_name': client_data['first_name'],
                    'last_name': client_data['last_name'],
                    'email': client_data['email']
                }
            )
            
            if created:
                user.set_password('123456')  # Senha padrão
                user.save()
                
                # Criar perfil de cliente
                cliente, cliente_created = Cliente.objects.get_or_create(
                    user=user,
                    defaults={'telefone': client_data['telefone']}
                )
                
                if cliente_created:
                    self.stdout.write(f'✅ Cliente criado: {user.get_full_name()}')
                else:
                    self.stdout.write(f'ℹ️  Cliente já existe: {user.get_full_name()}')
            else:
                self.stdout.write(f'ℹ️  Usuário já existe: {user.get_full_name()}')

    def _create_business_hours(self):
        """Cria horários de funcionamento"""
        business_hours_data = [
            # Segunda-feira
            {'day_of_week': 0, 'start_time': time(9, 0), 'end_time': time(18, 0)},
            # Terça-feira
            {'day_of_week': 1, 'start_time': time(9, 0), 'end_time': time(18, 0)},
            # Quarta-feira
            {'day_of_week': 2, 'start_time': time(9, 0), 'end_time': time(18, 0)},
            # Quinta-feira
            {'day_of_week': 3, 'start_time': time(9, 0), 'end_time': time(18, 0)},
            # Sexta-feira
            {'day_of_week': 4, 'start_time': time(9, 0), 'end_time': time(18, 0)},
            # Sábado
            {'day_of_week': 5, 'start_time': time(8, 0), 'end_time': time(17, 0)},
            # Domingo - não funciona
        ]
        
        for hour_data in business_hours_data:
            business_hour, created = BusinessHour.objects.get_or_create(
                day_of_week=hour_data['day_of_week'],
                defaults={
                    'start_time': hour_data['start_time'],
                    'end_time': hour_data['end_time'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    f'✅ Horário criado: {business_hour.get_day_of_week_display()} '
                    f'{business_hour.start_time} - {business_hour.end_time}'
                )
            else:
                self.stdout.write(
                    f'ℹ️  Horário já existe: {business_hour.get_day_of_week_display()}'
                ) 