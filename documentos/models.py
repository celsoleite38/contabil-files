import os
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings

class Setor(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome
    class Meta:
        verbose_name_plural = "Setores"

class Empresa(models.Model):
    nome_fantasia = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=14, unique=True)
    limite_usuarios = models.PositiveIntegerField(default=3)

    def __str__(self):
        return self.nome_fantasia



def caminho_resposta_cliente(instance, filename):
    # 1. Pegamos a data atual para formatar as pastas
    agora = timezone.now()
    ano = agora.strftime('%Y')  # Ex: 2026
    mes = agora.strftime('%m')  # Ex: 01
    
    nome_empresa = slugify(instance.empresa_destino.nome_fantasia)
    return f'pedidos/{ano}/{mes}/{nome_empresa}/{filename}'

class PedidoDocumento(models.Model):
    titulo = models.CharField(max_length=150)
    descricao_solicitacao = models.TextField()
    usuario_solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pedidos_feitos')
    empresa_destino = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='pedidos')
    setor_solicitante = models.ForeignKey(Setor, on_delete=models.CASCADE)
    
    # AJUSTE AQUI: Trocamos a string pelo nome da função
    arquivo_enviado = models.FileField(upload_to=caminho_resposta_cliente, null=True, blank=True)
    
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    concluido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.titulo} - {self.empresa_destino}"
    
class AgendamentoPedido(models.Model):
    REPETICAO_CHOICES = [
        ('UMA_VEZ', 'Uma vez'),
        ('DIARIO', 'Diário'),
        ('SEMANAL', 'Semanal'),
        ('MENSAL', 'Mensal'),
    ]

    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    usuario_solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    usuario_destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agendamentos_recebidos')
    data_agendada = models.DateField()
    repeticao = models.CharField(max_length=10, choices=REPETICAO_CHOICES, default='UMA_VEZ')
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} - {self.get_repeticao_display()}"