from django.contrib import admin
from .models import Service, BusinessHour, BarbershopInfo, Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefone', 'data_nascimento', 'created_at')
    list_filter = ('created_at', 'data_nascimento')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'telefone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações do Usuário', {
            'fields': ('user',)
        }),
        ('Informações Pessoais', {
            'fields': ('telefone', 'data_nascimento', 'endereco')
        }),
        ('Informações do Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)


@admin.register(BusinessHour)
class BusinessHourAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    list_editable = ('is_active',)


@admin.register(BarbershopInfo)
class BarbershopInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'whatsapp')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'logo')
        }),
        ('Contato', {
            'fields': ('phone', 'whatsapp', 'address')
        }),
        ('Redes Sociais', {
            'fields': ('instagram', 'facebook')
        }),
    )