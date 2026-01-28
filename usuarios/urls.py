from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Login / Logout
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/sucesso/', views.redirecionar_pos_login, name='redirecionar_pos_login'),

    # Gestão de Usuários
    path('novo/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('ativar/<str:token>/', views.ativar_conta, name='ativar_conta'),
    path('editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('excluir/<int:usuario_id>/', views.excluir_usuario, name='excluir_usuario'),
    path('senha/<int:usuario_id>/', views.alterar_senha_admin, name='alterar_senha_admin'),
]