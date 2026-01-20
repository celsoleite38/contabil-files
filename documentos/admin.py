from django.contrib import admin
from .models import Empresa, Setor, PedidoDocumento

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'cnpj', 'limite_usuarios')
    search_fields = ('nome_fantasia', 'cnpj')

@admin.register(PedidoDocumento)
class PedidoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'empresa_destino', 'setor_solicitante', 'concluido', 'data_solicitacao')
    list_filter = ('concluido', 'setor_solicitante', 'empresa_destino')
    search_fields = ('titulo',)