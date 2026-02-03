from django.shortcuts import render, redirect, get_object_or_404
from .forms import ConfiguracaoSistemaForm, CriarPedidoForm, ResponderPedidoForm, EmpresaForm, SetorForm, AgendamentoPedidoForm
from django.core.mail import send_mail, EmailMultiAlternatives
from .models import AgendamentoPedido, ConfiguracaoSistema, PedidoDocumento, Empresa, Setor
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.models import Usuario
from django.db.models import Count, Q
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
import os
from django.conf import settings


def manual_usuario(request):
    return render(request, 'documentos/manual.html')

def eh_contador_ou_admin(user):
    return user.tipo in ['CONTABILIDADE', 'ADMIN_CONTABILIDADE']

@login_required
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


def enviar_notificacao_documento(pedido, tipo_evento):
    config = ConfiguracaoSistema.objects.first()
    
    
    logo_url = "https://contabfiles.innosoft.com.br/static/img/logo2.png"
    if config and config.logo_contabilidade:
        dominio = "https://contabfiles.innosoft.com.br"
        logo_url = f"{dominio}{config.logo_contabilidade.url}"
    
    context = {
        'pedido': pedido,
        'logo_url': logo_url,
        'nome_contabilidade': config.nome_contabilidade if config else "Contabilidade",
        'link_sistema': 'https://contabfiles.innosoft.com.br/pedidos/'
    }
    
    if tipo_evento == 'SOLICITACAO':
        assunto = f"Solicitação: {pedido.titulo}"
        template = 'documentos/email_solicitacao.html'
        
        to_list = [pedido.usuario_destinatario.email]
        
        cc_list = []#pedido.usuario_solicitante.email
    else:
        assunto = f"Recibo de Envio: {pedido.titulo}"
        template = 'documentos/email_recibo.html'
        
        to_list = [pedido.usuario_destinatario.email, pedido.usuario_solicitante.email]
        cc_list = []
        
    nome_exibicao = config.nome_contabilidade if config and config.nome_contabilidade else "ContabFiles"

    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)
    from_email = f'{nome_exibicao} <suporteinnosoft@gmail.com>'
    
    
    email = EmailMultiAlternatives(assunto, text_content, from_email, to_list, cc=cc_list)
    email.attach_alternative(html_content, "text/html")
    
    try:
        # 1. Definimos o caminho do arquivo no VPS
        # Se estiver em static/img/logo2.png, usamos o BASE_DIR
        path_logo = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo2.png')
        
        # Se a logo for dinâmica (vinda do banco), descomente abaixo:
        # if config and config.logo_contabilidade:
        #     path_logo = config.logo_contabilidade.path

        with open(path_logo, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<logo_cid>') # Mesmo ID usado no context
            img.add_header('Content-Disposition', 'inline', filename='logo2.png')
            email.attach(img)
    except Exception as e:
        print(f"Não foi possível anexar a logo: {e}")
    
    try:
        email.send()
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

@login_required
def responder_pedido(request, pedido_id):
    pedido = get_object_or_404(PedidoDocumento, id=pedido_id)
    
    if request.user.tipo in ['CONTABILIDADE', 'ADMIN_CONTABILIDADE']:
        messages.warning(request, "A contabilidade não envia arquivos de resposta.")
        return redirect('lista_pedidos')

    if request.method == 'POST':
        form = ResponderPedidoForm(request.POST, request.FILES, instance=pedido)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.concluido = True
            pedido.save()

            
            enviar_notificacao_documento(pedido, 'RECIBO')
            
            return render(request, 'documentos/sucesso.html')
    else:
        form = ResponderPedidoForm(instance=pedido)
    return render(request, 'documentos/responder_pedido.html', {'pedido': pedido, 'form': form})


def criar_pedido_documento(request):
    if request.method == 'POST':
        form = CriarPedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.usuario_solicitante = request.user
            pedido.save()
            usuario_alvo = form.cleaned_data['usuario_destinatario']
           
            enviar_notificacao_documento(pedido, 'SOLICITACAO')
            
            messages.success(request, "Pedido criado e e-mail enviado ao cliente.")
            return redirect('lista_pedidos')
    else:
        form = CriarPedidoForm()
    return render(request, 'documentos/criar_pedido.html', {'form': form})

@login_required
def lista_pedidos(request):
    user = request.user
    UsuarioModel = get_user_model()
    
    empresa_id = request.GET.get('empresa')
    solicitante_id = request.GET.get('solicitante')
    destinatario_id = request.GET.get('destinatario')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    sort_by = request.GET.get('sort', '-data_solicitacao')
    
    empresas_todas = Empresa.objects.all().order_by('nome_fantasia')
   
    if user.tipo in ['CONTABILIDADE', 'ADMIN_CONTABILIDADE']:
        pedidos = PedidoDocumento.objects.filter(excluido=False)
        if empresa_id:
            pedidos = pedidos.filter(empresa_destino_id=empresa_id)
        
        
        usuarios_filtro = UsuarioModel.objects.filter(
            tipo__in=['CONTABILIDADE', 'ADMIN_CONTABILIDADE']
        ).exclude(username='innosoft').order_by('username')
    
    
    else:
        pedidos = PedidoDocumento.objects.filter(empresa_destino=user.empresa, excluido=False)
        usuarios_filtro = UsuarioModel.objects.filter(
            tipo__in=['CONTABILIDADE', 'ADMIN_CONTABILIDADE']
    ).exclude(username='innosoft').order_by('username')

    
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

@login_required
@user_passes_test(eh_contador_ou_admin)
def excluir_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(PedidoDocumento, id=pedido_id)
        
        if pedido.arquivo_enviado or pedido.concluido:
            messages.error(request, "Este pedido já foi atendido pelo cliente e não pode ser excluído.")
            return redirect('lista_pedidos')

        justificativa = request.POST.get('justificativa')

        if not justificativa or len(justificativa) < 5:
            messages.error(request, "Justificativa muito curta ou vazia!")
            return redirect('lista_pedidos')

        pedido.excluido = True
        pedido.justificativa_exclusao = justificativa
        pedido.usuario_exclusao = request.user
        pedido.save()
        
        messages.success(request, "Pedido arquivado como excluído.")
        
    return redirect('lista_pedidos')

@login_required
@user_passes_test(eh_contador_ou_admin)
def dashboard_admin(request):
    config = ConfiguracaoSistema.objects.first()
    total_empresas = Empresa.objects.count()
    total_setores = Setor.objects.count()
    total_usuarios = Usuario.objects.count()
    total_pedidos = PedidoDocumento.objects.filter(excluido=False).count()
    concluidos = PedidoDocumento.objects.filter(concluido=True).count()
    # Cálculo simples de porcentagem
    percentual = (concluidos / total_pedidos * 100) if total_pedidos > 0 else 0
    pedidos_excluidos = PedidoDocumento.objects.filter(excluido=True).order_by('-data_solicitacao')[:10]
    
    print(f"Total de excluídos encontrados: {pedidos_excluidos.count()}")
    
    relatorio_pendencias = Empresa.objects.annotate(
        ttotal_pedidos=Count('pedidos_empresa', filter=Q(pedidos_empresa__excluido=False)),
        pedidos_pendentes=Count(
            'pedidos_empresa', 
            filter=Q(pedidos_empresa__concluido=False, pedidos_empresa__excluido=False)
        )
    ).filter(pedidos_pendentes__gt=0).order_by('-pedidos_pendentes')
    
    return render(request, 'documentos/admin_dashboard.html', {
        'config': config,
        'total_empresas': total_empresas,
        'total_setores': total_setores,
        'total_usuarios': total_usuarios,
        'total_pedidos': total_pedidos,
        'percentual': percentual,
        'relatorio_pendencias': relatorio_pendencias,
        'pedidos_excluidos': pedidos_excluidos,
    })

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

@login_required
def editar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, f"Empresa {empresa.nome_fantasia} atualizada!")
            return redirect('cadastrar_empresa') # Ou a view onde fica a lista
    else:
        form = EmpresaForm(instance=empresa)
    
    return render(request, 'documentos/editar_empresa.html', {
        'form': form,
        'empresa': empresa
    })

@login_required
def excluir_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    # Opcional: verificar se há usuários vinculados antes de excluir
    nome = empresa.nome_fantasia
    empresa.delete()
    messages.success(request, f"Empresa {nome} removida com sucesso.")
    return redirect('cadastrar_empresa')



def editar_setor(request, setor_id):
    setor = get_object_or_404(Setor, id=setor_id)
    
    if request.method == 'POST':
        form = SetorForm(request.POST, instance=setor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Setor {setor.nome} atualizado com sucesso!")
            return redirect('cadastrar_setor')  # Redireciona de volta para a lista
    else:
        form = SetorForm(instance=setor)
    
    return render(request, 'documentos/editar_setor.html', {
        'form': form,
        'setor': setor,
        'titulo': 'Editar Setor'
    })

def excluir_setor(request, setor_id):
    setor = get_object_or_404(Setor, id=setor_id)
    nome_setor = setor.nome
    setor.delete()
    messages.success(request, f"Setor {nome_setor} excluído com sucesso!")
    return redirect('cadastrar_setor')

@login_required
@user_passes_test(lambda u: u.tipo == 'ADMIN_CONTABILIDADE')
def configurar_painel(request):
    # Pega a primeira configuração ou cria uma se não existir
    config, created = ConfiguracaoSistema.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = ConfiguracaoSistemaForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configurações atualizadas com sucesso!")
            return redirect('configurar_painel')
    else:
        form = ConfiguracaoSistemaForm(instance=config)

    return render(request, 'documentos/configuracoes.html', {
        'form': form,
        'config': config
    })
    
@login_required
@user_passes_test(eh_contador_ou_admin)
def central_exclusoes(request):
    # Captura os filtros do GET
    empresa_id = request.GET.get('empresa')
    usuario_id = request.GET.get('usuario')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # Query base: apenas os marcados como excluídos (soft delete)
    pedidos = PedidoDocumento.objects.filter(excluido=True)

    # Aplicação dos filtros
    if empresa_id:
        pedidos = pedidos.filter(empresa_destino_id=empresa_id)
    if usuario_id:
        pedidos = pedidos.filter(usuario_exclusao_id=usuario_id)
    if data_inicio:
        pedidos = pedidos.filter(data_solicitacao__date__gte=data_inicio)
    if data_fim:
        pedidos = pedidos.filter(data_solicitacao__date__lte=data_fim)

    pedidos = pedidos.order_by('-data_solicitacao')

    # Lógica para Exclusão Definitiva em Massa (Seleção)
    if request.method == 'POST' and 'excluir_definitivo' in request.POST:
        ids_para_excluir = request.POST.getlist('pedidos_selecionados')
        PedidoDocumento.objects.filter(id__in=ids_para_excluir, excluido=True).delete()
        messages.success(request, f"{len(ids_para_excluir)} pedidos foram removidos definitivamente.")
        return redirect('central_exclusoes')

    context = {
        'pedidos': pedidos,
        'empresas': Empresa.objects.all(),
        'usuarios': Usuario.objects.filter(tipo__in=['CONTABILIDADE', 'ADMIN_CONTABILIDADE']),
        'filtros': request.GET,
    }
    return render(request, 'documentos/central_exclusoes.html', context)