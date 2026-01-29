
from django.core.management.base import BaseCommand
from django.utils import timezone
from documentos.models import AgendamentoPedido, PedidoDocumento, Empresa
from datetime import timedelta

class Command(BaseCommand):
    help = 'Transforma agendamentos do dia em pedidos reais'

    def handle(self, *args, **kwargs):
        hoje = timezone.now().date()
        agendamentos = AgendamentoPedido.objects.filter(data_agendada=hoje, ativo=True)

        if not agendamentos.exists():
            self.stdout.write(self.style.WARNING('Nenhum agendamento para processar hoje.'))
            return

        for agend in agendamentos:
            # 1. Cria o pedido real
            PedidoDocumento.objects.create(
                titulo=agend.titulo,
                descricao_solicitacao=agend.descricao,
                usuario_solicitante=agend.usuario_solicitante,
                usuario_destinatario=agend.usuario_destinatario,
                # CORREÇÃO AQUI: usamos 'agend' (minúsculo), que é a instância atual
                empresa_destino=agend.empresa_destino,
                data_solicitacao=timezone.now()
            )

            # 2. Atualiza a próxima data
            if agend.repeticao == 'DIARIO':
                agend.data_agendada += timedelta(days=1)
            elif agend.repeticao == 'SEMANAL':
                agend.data_agendada += timedelta(weeks=1)
            elif agend.repeticao == 'MENSAL':
                # Somar 30 dias ou usar relativedelta para precisão de meses
                agend.data_agendada += timedelta(days=30)
            else:
                agend.ativo = False

            agend.save()

            # CORREÇÃO NO LOG: usar agend.empresa para mostrar o nome correto no terminal
            self.stdout.write(self.style.SUCCESS(f'Pedido criado para a empresa: {agend.empresa_destino.nome_fantasia}'))