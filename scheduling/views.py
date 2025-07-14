from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from datetime import date, time, datetime, timedelta
from .models import Appointment
from .forms import AppointmentForm
from core.models import BusinessHour, Cliente, Service
from core.utils import send_whatsapp_message, create_appointment_message, get_barbershop_whatsapp


def view_future_appointments(request):
    """
    View para visualizar agendamentos futuros
    """
    # Obter data atual
    today = timezone.now().date()
    
    # Filtrar agendamentos futuros (incluindo hoje)
    future_appointments = Appointment.objects.filter(
        date__gte=today,
        is_cancelled=False
    ).order_by('date', 'time')
    
    # Agrupar por data
    appointments_by_date = {}
    for appointment in future_appointments:
        date_str = appointment.date.strftime('%d/%m/%Y')
        if date_str not in appointments_by_date:
            appointments_by_date[date_str] = []
        appointments_by_date[date_str].append(appointment)
    
    # Estatísticas
    total_appointments = future_appointments.count()
    confirmed_appointments = future_appointments.filter(is_confirmed=True).count()
    pending_appointments = future_appointments.filter(is_confirmed=False).count()
    
    # Próximos 7 dias
    next_week = today + timedelta(days=7)
    next_week_appointments = future_appointments.filter(date__lte=next_week)
    
    context = {
        'appointments_by_date': appointments_by_date,
        'total_appointments': total_appointments,
        'confirmed_appointments': confirmed_appointments,
        'pending_appointments': pending_appointments,
        'next_week_appointments': next_week_appointments,
        'today': today,
        'next_week': next_week,
    }
    
    return render(request, 'scheduling/future_appointments.html', context)


@csrf_protect
def schedule_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            # Vincular ao cliente se estiver autenticado
            if request.user.is_authenticated and not request.user.is_staff:
                try:
                    appointment.cliente = request.user.cliente
                except Cliente.DoesNotExist:
                    # Se o cliente não existe, criar um
                    cliente = Cliente.objects.create(user=request.user)
                    appointment.cliente = cliente
            
            # Salvar o agendamento
            appointment.save()
            
            # Criar mensagem para WhatsApp
            whatsapp_message = create_appointment_message(appointment)
            whatsapp_url = send_whatsapp_message(get_barbershop_whatsapp(), whatsapp_message)
            
            messages.success(
                request,
                f'Agendamento realizado com sucesso! '
                f'Seu horário: {appointment.date.strftime("%d/%m/%Y")} às {appointment.time.strftime("%H:%M")}. '
                f'Entraremos em contato para confirmar.'
            )
            
            # Redirecionar baseado no tipo de usuário
            if request.user.is_authenticated and not request.user.is_staff:
                return redirect('cliente_dashboard')
            else:
                # Adicionar contexto com link do WhatsApp
                context = {
                    'appointment': appointment,
                    'whatsapp_url': whatsapp_url,
                    'whatsapp_message': whatsapp_message
                }
                return render(request, 'scheduling/success.html', context)
    else:
        form = AppointmentForm()
    
    context = {'form': form}
    return render(request, 'scheduling/schedule.html', context)


def appointment_success(request):
    return render(request, 'scheduling/success.html')


def get_available_times(request):
    """API endpoint para obter horários disponíveis"""
    selected_date = request.GET.get('date')
    service_id = request.GET.get('service')
    
    if not selected_date:
        return JsonResponse({'times': []})
    
    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'times': []})
    
    # Verificar se a data é válida
    if selected_date < date.today():
        return JsonResponse({'times': []})
    
    # Obter horários de funcionamento para o dia
    day_of_week = selected_date.weekday()
    business_hours = BusinessHour.objects.filter(
        day_of_week=day_of_week,
        is_active=True
    )
    
    if not business_hours.exists():
        return JsonResponse({'times': []})
    
    # Obter duração do serviço se especificado
    service_duration = 30  # duração padrão em minutos
    if service_id:
        try:
            service = Service.objects.get(id=service_id, is_active=True)
            service_duration = service.duration
        except Service.DoesNotExist:
            pass
    
    # Gerar horários disponíveis
    available_times = []
    for bh in business_hours:
        current_time = datetime.combine(selected_date, bh.start_time)
        end_time = datetime.combine(selected_date, bh.end_time)
        
        while current_time < end_time:
            time_str = current_time.strftime('%H:%M')
            time_obj = current_time.time()
            
            # Verificar se há tempo suficiente para o serviço
            service_end_time = (current_time + timedelta(minutes=service_duration)).time()
            if service_end_time > bh.end_time:
                break
            
            # Verificar se o horário não está ocupado
            is_occupied = Appointment.objects.filter(
                date=selected_date,
                time=time_obj,
                is_cancelled=False
            ).exists()
            
            # Verificar se não é no passado (para hoje)
            if selected_date == date.today():
                if time_obj <= datetime.now().time():
                    is_occupied = True
            
            if not is_occupied:
                available_times.append({
                    'time': time_str,
                    'display': f"{time_str} - {(current_time + timedelta(minutes=service_duration)).strftime('%H:%M')}"
                })
            
            # Avançar 30 minutos
            current_time += timedelta(minutes=30)
    
    return JsonResponse({'times': available_times})


@login_required
def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.is_confirmed = True
    appointment.save()
    
    # Enviar mensagem de confirmação para o cliente
    from core.utils import create_confirmation_message
    confirmation_message = create_confirmation_message(appointment)
    client_whatsapp_url = send_whatsapp_message(appointment.client_phone, confirmation_message)
    
    messages.success(
        request, 
        f'Agendamento de {appointment.client_name} confirmado. '
        f'Link para enviar confirmação: {client_whatsapp_url}'
    )
    return redirect('admin_dashboard')


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.is_cancelled = True
    appointment.save()
    messages.success(request, f'Agendamento de {appointment.client_name} cancelado.')
    return redirect('admin_dashboard')


@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agendamento reagendado com sucesso.')
            return redirect('admin_dashboard')
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
        'is_reschedule': True
    }
    return render(request, 'scheduling/reschedule.html', context)


@login_required
def send_whatsapp_notification(request, appointment_id):
    """
    View para enviar notificação WhatsApp para um agendamento específico
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Criar mensagem baseada no status do agendamento
    if appointment.is_confirmed:
        message = create_confirmation_message(appointment)
    else:
        message = create_appointment_message(appointment)
    
    # Gerar link do WhatsApp
    whatsapp_url = send_whatsapp_message(appointment.client_phone, message)
    
    messages.success(
        request, 
        f'Link do WhatsApp gerado para {appointment.client_name}: {whatsapp_url}'
    )
    
    return redirect('admin_dashboard')