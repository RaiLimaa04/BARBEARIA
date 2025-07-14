import urllib.parse
from django.conf import settings
from .models import BarbershopInfo


def send_whatsapp_message(phone_number, message):
    """
    Envia uma mensagem para o WhatsApp usando a API do WhatsApp Web
    """
    # Remove caracteres especiais do número de telefone
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    
    # Adiciona código do país se não estiver presente
    if not clean_phone.startswith('55'):
        clean_phone = '55' + clean_phone
    
    # Codifica a mensagem para URL
    encoded_message = urllib.parse.quote(message)
    
    # Cria o link do WhatsApp
    whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
    
    return whatsapp_url


def get_barbershop_whatsapp():
    """
    Retorna o número de WhatsApp da barbearia
    """
    try:
        barbershop_info = BarbershopInfo.objects.first()
        if barbershop_info and barbershop_info.whatsapp:
            return barbershop_info.whatsapp
    except:
        pass
    
    # Fallback para o número fornecido
    return "(87) 98161-3777"


def create_appointment_message(appointment):
    """
    Cria a mensagem de agendamento para enviar via WhatsApp
    """
    message = f"""🪒 *Novo Agendamento*

👤 *Cliente:* {appointment.client_name}
📞 *Telefone:* {appointment.client_phone}
✂️ *Serviço:* {appointment.service.name}
📅 *Data:* {appointment.date.strftime('%d/%m/%Y')}
⏰ *Horário:* {appointment.time.strftime('%H:%M')}
💰 *Valor:* R$ {appointment.service.price}

📝 *Observações:* {appointment.notes if appointment.notes else 'Nenhuma'}

---
*Sistema de Agendamento Barbearia*"""
    
    return message


def create_confirmation_message(appointment):
    """
    Cria a mensagem de confirmação para enviar ao cliente
    """
    message = f"""✅ *Agendamento Confirmado!*

Olá {appointment.client_name}! 

Seu agendamento foi *CONFIRMADO*:

✂️ *Serviço:* {appointment.service.name}
📅 *Data:* {appointment.date.strftime('%d/%m/%Y')}
⏰ *Horário:* {appointment.time.strftime('%H:%M')}
💰 *Valor:* R$ {appointment.service.price}

📍 *Local:* [Endereço da Barbearia]

⚠️ *Importante:*
• Chegue com 10 minutos de antecedência
• Traga documentos se necessário
• Em caso de cancelamento, avise com antecedência

📞 *Dúvidas:* {get_barbershop_whatsapp()}

Obrigado por escolher nossos serviços! 🙏"""
    
    return message 