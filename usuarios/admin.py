from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Adicionamos nossos campos personalizados ao formulário do Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Informações do Sistema', {'fields': ('tipo', 'empresa', 'setor', 'is_ativado', 'token_ativacao')}),
    )
    list_display = ('username', 'email', 'tipo', 'empresa', 'setor', 'is_ativado')
    list_filter = ('tipo', 'is_ativado')