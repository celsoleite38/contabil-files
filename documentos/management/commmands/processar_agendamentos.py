from django.core.management.base import BaseCommand
from django.utils import timezone
from documentos.models import AgendamentoPedido, PedidoDocumento
from datetime import timedelta

class Command(BaseCommand):
    help = 'Transforma agendamentos do dia em pedidos reais'

    def handle(self, *args, **kwargs):
        hoje = timezone.now().date()
        agendamentos = AgendamentoPedido.objects.filter(data_agendada=hoje, ativo=True)

        for agend in agendamentos:
            # 1. Cria o pedido real que o cliente vê
            PedidoDocumento.objects.create(
                titulo=agend.titulo,
                descricao_solicitacao=agend.descricao,
                usuario_solicitante=agend.usuario_solicitante,
                usuario_destinatario=agend.usuario_destinatario,
                # Aqui você preencheria os outros campos como empresa_destino, etc.
            )

            # 2. Atualiza a próxima data se houver repetição
            if agend.repeticao == 'DIARIO':
                agend.data_agendada += timedelta(days=1)
            elif agend.repeticao == 'SEMANAL':
                agend.data_agendada += timedelta(weeks=1)
            elif agend.repeticao == 'MENSAL':
                # Lógica simplificada para próximo mês
                agend.data_agendada = agend.data_agendada + timedelta(days=30)
            else:
                agend.ativo = False # Se for 'UMA_VEZ', desativa
            
            agend.save()
        
        self.stdout.write(self.style.SUCCESS('Agendamentos processados!'))