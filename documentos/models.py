from django.db import models

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

class PedidoDocumento(models.Model):
    titulo = models.CharField(max_length=150)
    descricao_solicitacao = models.TextField()
    empresa_destino = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='pedidos')
    setor_solicitante = models.ForeignKey(Setor, on_delete=models.CASCADE)
    
    # Arquivo que o cliente enviará como resposta
    arquivo_enviado = models.FileField(upload_to='pedidos/%Y/%m/', null=True, blank=True)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    concluido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.titulo} - {self.empresa_destino}"