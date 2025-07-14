from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('servicos/', views.services, name='services'),
    path('contato/', views.contact, name='contact'),
    
    # URLs para clientes
    path('cliente/login/', views.cliente_login, name='cliente_login'),
    path('cliente/register/', views.cliente_register, name='cliente_register'),
    path('cliente/dashboard/', views.cliente_dashboard, name='cliente_dashboard'),
    path('cliente/logout/', views.cliente_logout, name='cliente_logout'),
    
    # URLs para administradores (mudando de admin/ para painel/)
    path('painel/login/', views.admin_login, name='admin_login'),
    path('painel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('painel/logout/', views.admin_logout, name='admin_logout'),
]