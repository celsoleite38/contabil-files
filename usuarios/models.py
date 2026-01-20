from django.db import models
from django.contrib.auth.models import AbstractUser
from documentos.models import Empresa, Setor

class Usuario(AbstractUser):
    TIPO_CHOICES = [
        ('CONTABILIDADE', 'Funcionário Contabilidade'),
        ('ADMIN_CONTABILIDADE', 'Administrador Contabilidade'),
        ('CLIENTE', 'Cliente/Empresa'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='CLIENTE')
    email = models.EmailField(unique=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True, related_name='usuarios_empresa')
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios_setor')
    
    is_ativado = models.BooleanField(default=False)
    token_ativacao = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"