from django.contrib import admin
from .models import Empresa, Setor, PedidoDocumento,AgendamentoPedido
from .models import ConfiguracaoSistema

admin.site.register(ConfiguracaoSistema)

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'cnpj', 'limite_usuarios')
    search_fields = ('nome_fantasia', 'cnpj')

@admin.register(PedidoDocumento)
class PedidoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'empresa_destino', 'setor_solicitante', 'concluido', 'data_solicitacao','excluido')
    list_filter = ('excluido','concluido', 'setor_solicitante', 'empresa_destino')
    search_fields = ('titulo','justificativa_exclusao', 'descricao_solicitacao', 'usuario_solicitante__username', 'usuario_destinatario__username')
    fields = ('titulo', 'descricao_solicitacao', 'empresa_destino', 'usuario_solicitante', 'usuario_destinatario', 'arquivo_enviado', 'concluido', 'excluido', 'justificativa_exclusao')
    


@admin.register(AgendamentoPedido)
class AgendamentoPedidoAdmin(admin.ModelAdmin):
    # Colunas que aparecerão na listagem
    list_display = ('titulo', 'empresa_destino', 'data_agendada', 'repeticao', 'ativo')
    
    # Filtros laterais para facilitar a busca
    list_filter = ('ativo', 'repeticao', 'data_agendada', 'empresa_destino')
    
    # Campos de busca (útil quando tiver muitos agendamentos)
    search_fields = ('titulo', 'descricao')
    
    # Organização das datas no topo para navegação rápida
    date_hierarchy = 'data_agendada'