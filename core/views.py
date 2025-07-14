from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from datetime import date, timedelta
from .models import Service, BarbershopInfo
from .forms import ClienteRegistrationForm, ClienteLoginForm, AdminLoginForm
from scheduling.models import Appointment


def home(request):
    barbershop_info = BarbershopInfo.objects.first()
    services = Service.objects.filter(is_active=True)
    
    context = {
        'barbershop_info': barbershop_info,
        'services': services,
    }
    return render(request, 'core/home.html', context)


def services(request):
    services = Service.objects.filter(is_active=True)
    context = {'services': services}
    return render(request, 'core/services.html', context)


def contact(request):
    barbershop_info = BarbershopInfo.objects.first()
    context = {'barbershop_info': barbershop_info}
    return render(request, 'core/contact.html', context)


@csrf_protect
def cliente_login(request):
    if request.user.is_authenticated:
        return redirect('cliente_dashboard')
    
    if request.method == 'POST':
        form = ClienteLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None and not user.is_staff:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                return redirect('cliente_dashboard')
            else:
                messages.error(request, 'Usuário ou senha incorretos.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ClienteLoginForm()
    
    return render(request, 'core/cliente_login.html', {'form': form})


@csrf_protect
def cliente_register(request):
    if request.user.is_authenticated:
        return redirect('cliente_dashboard')
    
    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Bem-vindo!')
            return redirect('cliente_dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ClienteRegistrationForm()
    
    return render(request, 'core/cliente_register.html', {'form': form})


@login_required
def cliente_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Buscar agendamentos do cliente
    appointments = Appointment.objects.filter(
        cliente=request.user.cliente,
        is_cancelled=False
    ).order_by('-date', '-time')
    
    # Agendamentos futuros
    future_appointments = appointments.filter(date__gte=date.today())
    
    # Agendamentos passados
    past_appointments = appointments.filter(date__lt=date.today())
    
    context = {
        'future_appointments': future_appointments,
        'past_appointments': past_appointments,
        'cliente': request.user.cliente,
    }
    
    return render(request, 'core/cliente_dashboard.html', context)


def cliente_logout(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('home')


@csrf_protect
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Usuário ou senha incorretos.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AdminLoginForm()
    
    return render(request, 'core/admin_login.html', {'form': form})


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('cliente_dashboard')
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Agendamentos de hoje
    today_appointments = Appointment.objects.filter(
        date=today,
        is_cancelled=False
    ).order_by('time')
    
    # Agendamentos de amanhã
    tomorrow_appointments = Appointment.objects.filter(
        date=tomorrow,
        is_cancelled=False
    ).order_by('time')
    
    # Estatísticas
    total_appointments_today = today_appointments.count()
    confirmed_appointments = today_appointments.filter(is_confirmed=True).count()
    pending_appointments = today_appointments.filter(is_confirmed=False).count()
    
    context = {
        'today_appointments': today_appointments,
        'tomorrow_appointments': tomorrow_appointments,
        'total_appointments_today': total_appointments_today,
        'confirmed_appointments': confirmed_appointments,
        'pending_appointments': pending_appointments,
        'today': today,
        'tomorrow': tomorrow,
    }
    
    return render(request, 'core/admin_dashboard.html', context)


def admin_logout(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('home') 