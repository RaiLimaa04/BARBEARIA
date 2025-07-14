from django.urls import path
from . import views

urlpatterns = [
    path('', views.schedule_appointment, name='schedule_appointment'),
    path('sucesso/', views.appointment_success, name='appointment_success'),
    path('api/available-times/', views.get_available_times, name='available_times'),
    path('confirmar/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('cancelar/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('reagendar/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('whatsapp/<int:appointment_id>/', views.send_whatsapp_notification, name='send_whatsapp_notification'),
    path('futuros/', views.view_future_appointments, name='future_appointments'),
]