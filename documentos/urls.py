from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views
from usuarios.views import cadastrar_usuario, ativar_conta, redirecionar_pos_login

urlpatterns = [
    # 1. Raiz do site redireciona para login
    path('', RedirectView.as_view(url='/login/'), name='index'),

      # 2. Gestão e Pedidos
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedidos/novo/', views.criar_pedido_documento, name='criar_pedido'),
    path('pedidos/responder/<int:pedido_id>/', views.responder_pedido, name='responder_pedido'),
    path('gestao/', views.dashboard_admin, name='dashboard_admin'),
    path('gestao/empresa/nova/', views.cadastrar_empresa, name='cadastrar_empresa'),
    path('gestao/setor/novo/', views.cadastrar_setor, name='cadastrar_setor'),
    path('usuarios/novo/', cadastrar_usuario, name='cadastrar_usuario'), 
    path('usuarios/ativar/<str:token>/', ativar_conta, name='ativar_conta'),
    path('login/sucesso/', redirecionar_pos_login, name='redirecionar_pos_login'),
    path('agendar/', views.agendar_pedido, name='agendar_pedido'),
    path('agendamentos/', views.lista_agendamentos, name='lista_agendamentos'),
    
]