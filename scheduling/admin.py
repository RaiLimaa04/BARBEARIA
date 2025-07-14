from django.contrib import admin
from .models import Appointment
from django.utils import timezone

class FutureAppointmentsFilter(admin.SimpleListFilter):
    title = 'Agendamentos Futuros'
    parameter_name = 'futuros'

    def lookups(self, request, model_admin):
        return (
            ('futuros', 'Somente futuros (a partir de hoje)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'futuros':
            return queryset.filter(date__gte=timezone.now().date())
        return queryset

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'service', 'date', 'time', 'status', 'created_at']
    list_filter = ['service', 'date', 'is_confirmed', 'is_cancelled', FutureAppointmentsFilter]
    search_fields = ['client_name', 'client_phone']
    date_hierarchy = 'date'
    list_per_page = 50
    
    def status(self, obj):
        return obj.status
    
    actions = ['confirm_appointments', 'cancel_appointments']
    
    def confirm_appointments(self, request, queryset):
        updated = queryset.update(is_confirmed=True, is_cancelled=False)
        self.message_user(request, f'{updated} agendamentos confirmados.')
    confirm_appointments.short_description = 'Confirmar agendamentos selecionados'
    
    def cancel_appointments(self, request, queryset):
        updated = queryset.update(is_cancelled=True)
        self.message_user(request, f'{updated} agendamentos cancelados.')
    cancel_appointments.short_description = 'Cancelar agendamentos selecionados'