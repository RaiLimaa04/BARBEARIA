from django.core.management.base import BaseCommand
from core.models import BarbershopInfo


class Command(BaseCommand):
    help = 'Configura o número de WhatsApp da barbearia'

    def add_arguments(self, parser):
        parser.add_argument(
            '--whatsapp',
            type=str,
            default='(87) 98161-3777',
            help='Número de WhatsApp da barbearia'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Barbearia São João',
            help='Nome da barbearia'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='(87) 98161-3777',
            help='Telefone da barbearia'
        )

    def handle(self, *args, **options):
        whatsapp = options['whatsapp']
        name = options['name']
        phone = options['phone']
        
        # Criar ou atualizar informações da barbearia
        barbershop_info, created = BarbershopInfo.objects.get_or_create(
            id=1,
            defaults={
                'name': name,
                'description': 'Barbearia tradicional com serviços de qualidade',
                'phone': phone,
                'whatsapp': whatsapp,
                'address': 'Endereço da barbearia será configurado posteriormente',
            }
        )
        
        if not created:
            barbershop_info.whatsapp = whatsapp
            barbershop_info.name = name
            barbershop_info.phone = phone
            barbershop_info.save()
            self.stdout.write(
                self.style.SUCCESS(f'Informações da barbearia atualizadas! WhatsApp: {whatsapp}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Informações da barbearia criadas! WhatsApp: {whatsapp}')
            ) 