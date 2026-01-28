import uuid
from django.shortcuts import render, redirect,  get_object_or_404
from django.core.mail import send_mail
from .models import Usuario
from .forms import CadastroUsuarioForm, EditarUsuarioForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm


def cadastrar_usuario(request):
    # 1. Capturamos o valor da busca logo no início (se não houver, fica vazio '')
    busca = request.GET.get('search', '')

    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_ativado = False
            user.token_ativacao = str(uuid.uuid4())
            user.save()
            
            link = f"http://127.0.0.1:8000/usuarios/ativar/{user.token_ativacao}/"
            
            send_mail(
                'Ative sua conta - Contabilidade',
                f'Olá, clique no link para ativar seu acesso: {link}',
                'contato@contabilidade.com',
                [user.email],
            )
            return render(request, 'usuarios/cadastro_sucesso.html')
        # Se o form for INVÁLIDO, ele não entra no IF e mantém os erros no 'form'
    else:
        # Se for GET (carregamento inicial), cria um formulário vazio
        form = CadastroUsuarioForm()

    # 2. Lógica de Listagem Unificada
    base_usuarios = Usuario.objects.select_related('empresa', 'setor').exclude(username='innosoft')

    if busca:
        base_usuarios = base_usuarios.filter(
            Q(username__icontains=busca) | 
            Q(email__icontains=busca) | 
            Q(empresa__nome_fantasia__icontains=busca) |
            Q(first_name__icontains=busca) |
            Q(last_name__icontains=busca) 
        )

    # Ordenamos para que a Contabilidade apareça primeiro e depois as Empresas
    usuarios_list = base_usuarios.order_by('tipo', 'empresa__nome_fantasia', 'username')

    # 3. Retorno Único para cadastro.html
    return render(request, 'usuarios/cadastro.html', {
        'form': form,
        'usuarios_list': usuarios_list, 
        'busca': busca
    })


def ativar_conta(request, token):
    try:
        user = Usuario.objects.get(token_ativacao=token)
        user.is_ativado = True
        user.is_active = True # Ativa o usuário para o login do Django
        user.token_ativacao = None # Limpa o token por segurança
        user.save()
        return render(request, 'usuarios/ativacao_sucesso.html')
    except Usuario.DoesNotExist:
        return render(request, 'usuarios/ativacao_erro.html')
    
def redirecionar_pos_login(request):
    if request.user.tipo == 'ADMIN_CONTABILIDADE':
        return redirect('dashboard_admin')
    elif request.user.tipo == 'CONTABILIDADE':
        return redirect('lista_pedidos')
    else:
        return redirect('lista_pedidos')
    
@login_required
def redirecionar_usuario(request):
    if request.user.tipo == 'ADMIN_CONTABILIDADE':
        return redirect('dashboard_admin')
    return redirect('lista_pedidos')




# View para Excluir Usuário
@login_required
def excluir_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if usuario.username != 'innosoft':  # Proteção para não excluir o admin principal
        usuario.delete()
        messages.success(request, "Usuário excluído com sucesso.")
    return redirect('cadastrar_usuario')

# View para Editar Dados (Placeholder por enquanto)


def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Formulário de Dados
    form = EditarUsuarioForm(instance=usuario)
    # Formulário de Senha (vazio para o Modal)
    form_senha = SetPasswordForm(user=usuario)

    if request.method == 'POST':
        # Verifica qual formulário foi enviado
        if 'btn_salvar_dados' in request.POST:
            form = EditarUsuarioForm(request.POST, instance=usuario)
            if form.is_valid():
                form.save()
                messages.success(request, "Dados atualizados!")
                return redirect('editar_usuario', usuario_id=usuario.id)
        
        elif 'btn_mudar_senha' in request.POST:
            form_senha = SetPasswordForm(user=usuario, data=request.POST)
            if form_senha.is_valid():
                form_senha.save()
                messages.success(request, "Senha alterada com sucesso!")
                return redirect('editar_usuario', usuario_id=usuario.id)

    return render(request, 'usuarios/editar_usuario.html', {
        'form': form,
        'form_senha': form_senha,
        'usuario': usuario
    })

# View para trocar senha (chamada pelo botão dentro da edição)
def alterar_senha_admin(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = SetPasswordForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Senha de {usuario.username} alterada!")
            return redirect('editar_usuario', usuario_id=usuario.id)
    else:
        form = SetPasswordForm(usuario)
    
    return render(request, 'usuarios/alterar_senha.html', {'form': form, 'usuario': usuario})