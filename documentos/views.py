from django.shortcuts import render, redirect, get_object_or_404
from .forms import CriarPedidoForm, ResponderPedidoForm, EmpresaForm, SetorForm, AgendamentoPedidoForm
from django.core.mail import send_mail
from .models import AgendamentoPedido, PedidoDocumento, Empresa, Setor
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.models import Usuario
from django.db.models import Count, Q
from django.http import JsonResponse
from django.contrib.auth import get_user_model


def lista_documentos(request):
    # Lista apenas os documentos da empresa do usuário logado
    docs = Documento.objects.filter(empresa__usuarios=request.user)
    return render(request, 'documentos/lista.html', {'docs': docs})

def upload_arquivo(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            # Aqui vinculamos automaticamente à empresa do usuário
            doc.empresa = request.user.empresas.first() 
            doc.save()
            return redirect('lista_documentos')
    else:
        form = DocumentoForm()
    return render(request, 'documentos/upload.html', {'form': form})


def responder_pedido(request, pedido_id):
    pedido = get_object_or_404(PedidoDocumento, id=pedido_id)
    
    if request.method == 'POST':
        arquivo = request.FILES.get('arquivo_enviado')
        if arquivo:
            pedido.arquivo_enviado = arquivo
            pedido.concluido = True
            pedido.save()

            # Envio de Recibo (Para Cliente e Contador)
            assunto = f"Recibo: {pedido.titulo} enviado com sucesso"
            mensagem = f"O documento {pedido.titulo} foi recebido pelo sistema."
            
            # Lista de e-mails: do cliente logado e de quem solicitou (se houver)
            destinatarios = [request.user.email] 
            
            send_mail(assunto, mensagem, 'sistema@contabilidade.com', destinatarios)
            
            return render(request, 'documentos/sucesso.html')
            
    return render(request, 'documentos/responder_pedido.html', {'pedido': pedido})

def criar_pedido_documento(request):
    if request.method == 'POST':
        form = CriarPedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.usuario_solicitante = request.user
            pedido.save()
            usuario_alvo = form.cleaned_data['usuario_destinatario']
            
            # Envia e-mail para o cliente avisando do novo pedido
            send_mail(
                f"Solicitação: {pedido.titulo}",
                f"Olá {usuario_alvo.username}, a contabilidade solicita: {pedido.descricao_solicitacao}",
                'sistema@contabilidade.com',
                [usuario_alvo.email],
            )
            return redirect('lista_pedidos')
    else:
        form = CriarPedidoForm()
    return render(request, 'documentos/criar_pedido.html', {'form': form})

# View para o Cliente Enviar o arquivo (Responder)
def responder_pedido(request, pedido_id):
    pedido = get_object_or_404(PedidoDocumento, id=pedido_id)
    
    if request.method == 'POST':
        form = ResponderPedidoForm(request.POST, request.FILES, instance=pedido)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.concluido = True
            pedido.save()

            # Envia recibo para o Cliente e Notificação para a Contabilidade
            destinatarios = [request.user.email] # Adicione o e-mail do contador se desejar
            send_mail(
                "Recibo de Envio",
                f"O documento {pedido.titulo} foi entregue com sucesso.",
                'sistema@contabilidade.com',
                destinatarios,
            )
            return render(request, 'documentos/sucesso.html')
    else:
        form = ResponderPedidoForm(instance=pedido)
    return render(request, 'documentos/responder_pedido.html', {'pedido': pedido, 'form': form})

@login_required
def lista_pedidos(request):
    user = request.user
    UsuarioModel = get_user_model()
    
    # Captura de parâmetros
    empresa_id = request.GET.get('empresa')
    solicitante_id = request.GET.get('solicitante')
    destinatario_id = request.GET.get('destinatario')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    sort_by = request.GET.get('sort', '-data_solicitacao')
    
    empresas_todas = Empresa.objects.all().order_by('nome_fantasia')

    # --- LÓGICA DE FILTRO DE USUÁRIOS (SOLICITANTES) ---
    # Se for contabilidade, vê todos os funcionários internos (exceto innosoft)
    if user.tipo in ['CONTABILIDADE', 'ADMIN_CONTABILIDADE']:
        pedidos = PedidoDocumento.objects.all()
        if empresa_id:
            pedidos = pedidos.filter(empresa_destino_id=empresa_id)
        
        # Filtra apenas quem é da contabilidade e remove o innosoft
        usuarios_filtro = UsuarioModel.objects.filter(
            tipo__in=['CONTABILIDADE', 'ADMIN_CONTABILIDADE']
        ).exclude(username='innosoft').order_by('username')
    
    # Se for cliente, vê apenas os usuários da própria empresa (exceto innosoft)
    else:
        pedidos = PedidoDocumento.objects.filter(empresa_destino=user.empresa)
        usuarios_filtro = UsuarioModel.objects.filter(
            tipo__in=['CONTABILIDADE', 'ADMIN_CONTABILIDADE']
    ).exclude(username='innosoft').order_by('username')

    # --- FILTROS DA TABELA ---
    if solicitante_id:
        pedidos = pedidos.filter(usuario_solicitante_id=solicitante_id)
    if destinatario_id:
        pedidos = pedidos.filter(usuario_destinatario_id=destinatario_id)
    if data_inicio:
        pedidos = pedidos.filter(data_solicitacao__date__gte=data_inicio)
    if data_fim:
        pedidos = pedidos.filter(data_solicitacao__date__lte=data_fim)

    # Ordenação
    campos_validos = ['titulo', 'usuario_solicitante__username', 'usuario_destinatario__username', 'concluido', 'data_solicitacao']
    if sort_by.lstrip('-') not in campos_validos:
        sort_by = '-data_solicitacao'
    
    pedidos = pedidos.order_by(sort_by)
    
    return render(request, 'documentos/lista_pedidos.html', {
        'pedidos': pedidos,
        'empresas_todas': empresas_todas,
        'usuarios_filtro': usuarios_filtro,
        'empresa_filtrada': empresa_id,
        'current_sort': sort_by,
        'filtros': request.GET 
    })

# Função para verificar se o usuário é da Contabilidade
def eh_contador_ou_admin(user):
    return user.tipo in ['CONTABILIDADE', 'ADMIN_CONTABILIDADE']

@login_required
@user_passes_test(eh_contador_ou_admin)
def dashboard_admin(request):
    total_empresas = Empresa.objects.count()
    total_setores = Setor.objects.count()
    total_usuarios = Usuario.objects.count()
    total_pedidos = PedidoDocumento.objects.count()
    concluidos = PedidoDocumento.objects.filter(concluido=True).count()
    # Cálculo simples de porcentagem para o gráfico CSS
    percentual = (concluidos / total_pedidos * 100) if total_pedidos > 0 else 0
    
    relatorio_pendencias = Empresa.objects.annotate(
        total_pedidos=Count('pedidos_empresa'),
        pedidos_pendentes=Count('pedidos_empresa', filter=Q(pedidos_empresa__concluido=False))
    ).filter(pedidos_pendentes__gt=0).order_by('-pedidos_pendentes')
    
    return render(request, 'documentos/admin_dashboard.html', {
        'total_empresas': total_empresas,
        'total_setores': total_setores,
        'total_usuarios': total_usuarios,
        'relatorio_pendencias': relatorio_pendencias,
    })

# Exemplo de listagem para o contador gerir
@login_required
@user_passes_test(eh_contador_ou_admin)
def gerir_empresas(request):
    empresas = Empresa.objects.all()
    return render(request, 'documentos/gerir_empresas.html', {'empresas': empresas})



@login_required
@user_passes_test(eh_contador_ou_admin)
def cadastrar_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_empresa')
    else:
        form = EmpresaForm()
    
    listagem = Empresa.objects.all().order_by('nome_fantasia')
    return render(request, 'documentos/form_generico.html', {
        'form': form,
        'titulo': 'Cadastrar Empresa',
        'listagem': listagem,
        'tipo': 'EMPRESA'
    })

@login_required
@user_passes_test(eh_contador_ou_admin)
def cadastrar_setor(request):
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_admin')
    else:
        form = SetorForm()

    listagem = Setor.objects.all().order_by('nome')
    return render(request, 'documentos/form_generico.html', {
        'form': SetorForm(),
        'titulo': 'Gerenciar Setores',
        'listagem': listagem,
        'tipo': 'SETOR'
    })
    


@login_required
def agendar_pedido(request):
    # Apenas funcionários da contabilidade podem agendar
    if request.user.tipo != 'CONTABILIDADE':
        return redirect('lista_pedidos')

    if request.method == 'POST':
        form = AgendamentoPedidoForm(request.POST)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.usuario_solicitante = request.user
            agendamento.save()
            return redirect('lista_agendamentos')
    else:
        form = AgendamentoPedidoForm()
    
    return render(request, 'documentos/agendar_pedido.html', {'form': form})

@login_required
def lista_agendamentos(request):
    agendamentos = AgendamentoPedido.objects.filter(ativo=True).order_by('data_agendada')
    return render(request, 'documentos/lista_agendamentos.html', {'agendamentos': agendamentos})



User = get_user_model()
def carregar_usuarios_empresa(request):
    empresa_id = request.GET.get('empresa_id')
    # Ajuste o filtro abaixo conforme o nome do campo de relação no seu modelo de Usuário
    usuarios = User.objects.filter(empresa_id=empresa_id).values('id', 'username')
    return JsonResponse(list(usuarios), safe=False)