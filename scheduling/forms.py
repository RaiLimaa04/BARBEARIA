from django import forms
from django.core.exceptions import ValidationError
from datetime import date, time, datetime, timedelta
from .models import Appointment
from core.models import Service, BusinessHour


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['client_name', 'client_phone', 'service', 'date', 'time']
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Digite seu nome completo'
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '(11) 99999-9999'
            }),
            'service': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control form-control-lg',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'time': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'time-select'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['service'].empty_label = 'Selecione um serviço'
        
        # Configurar o campo time como um select vazio inicialmente
        self.fields['time'].choices = [('', 'Selecione uma data primeiro')]
        self.fields['time'].required = False

    def clean_date(self):
        date_value = self.cleaned_data.get('date')
        if date_value and date_value < date.today():
            raise ValidationError('Não é possível agendar para datas passadas.')
        return date_value

    def clean_time(self):
        time_value = self.cleaned_data.get('time')
        date_value = self.cleaned_data.get('date')
        
        if date_value and time_value:
            # Verificar se é hoje e o horário já passou
            if date_value == date.today() and time_value < datetime.now().time():
                raise ValidationError('Não é possível agendar para horários que já passaram.')
            
            # Verificar se o horário está dentro do funcionamento
            day_of_week = date_value.weekday()
            business_hours = BusinessHour.objects.filter(
                day_of_week=day_of_week,
                is_active=True
            )
            
            if not business_hours.exists():
                raise ValidationError('Não funcionamos neste dia da semana.')
            
            valid_time = False
            for bh in business_hours:
                if bh.start_time <= time_value <= bh.end_time:
                    valid_time = True
                    break
            
            if not valid_time:
                raise ValidationError('Horário fora do funcionamento.')
        
        return time_value

    def clean(self):
        cleaned_data = super().clean()
        date_value = cleaned_data.get('date')
        time_value = cleaned_data.get('time')
        
        if date_value and time_value:
            # Verificar se já existe agendamento para este horário
            existing_appointment = Appointment.objects.filter(
                date=date_value,
                time=time_value,
                is_cancelled=False
            ).exists()
            
            if existing_appointment:
                raise ValidationError('Este horário já está ocupado. Escolha outro horário.')
        
        return cleaned_data