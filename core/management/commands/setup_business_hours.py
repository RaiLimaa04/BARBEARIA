from django.core.management.base import BaseCommand
from core.models import BusinessHour
from datetime import time


class Command(BaseCommand):
    help = 'Configura os horários de funcionamento da barbearia'

    def handle(self, *args, **options):
        # Limpar horários existentes
        BusinessHour.objects.all().delete()
        
        # Configurar horários conforme especificado
        business_hours = [
            # Segunda-feira (0)
            {'day_of_week': 0, 'start_time': time(9, 0), 'end_time': time(19, 0)},
            # Terça-feira (1)
            {'day_of_week': 1, 'start_time': time(9, 0), 'end_time': time(19, 0)},
            # Quarta-feira (2)
            {'day_of_week': 2, 'start_time': time(9, 0), 'end_time': time(19, 0)},
            # Quinta-feira (3)
            {'day_of_week': 3, 'start_time': time(9, 0), 'end_time': time(19, 0)},
            # Sexta-feira (4)
            {'day_of_week': 4, 'start_time': time(9, 0), 'end_time': time(19, 0)},
            # Sábado (5)
            {'day_of_week': 5, 'start_time': time(8, 0), 'end_time': time(17, 0)},
            # Domingo (6) - Fechado (não será criado)
        ]
        
        created_count = 0
        for hour_data in business_hours:
            business_hour, created = BusinessHour.objects.get_or_create(
                day_of_week=hour_data['day_of_week'],
                defaults={
                    'start_time': hour_data['start_time'],
                    'end_time': hour_data['end_time'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Horário criado: {business_hour.get_day_of_week_display()} - '
                        f'{business_hour.start_time} às {business_hour.end_time}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Configuração concluída! {created_count} horários de funcionamento criados.'
            )
        ) 