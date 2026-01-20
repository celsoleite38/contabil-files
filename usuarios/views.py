import uuid
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import CadastroUsuarioForm
from django.contrib.auth.decorators import login_required


def cadastrar_usuario(request): 
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_ativado = False
            user.token_ativacao = str(uuid.uuid4())
            user.save()
            
            # Link de ativação (simulado para o console)
            link = f"http://127.0.0.1:8000/usuarios/ativar/{user.token_ativacao}/"
            
            send_mail(
                'Ative sua conta - Contabilidade',
                f'Olá, clique no link para ativar seu acesso: {link}',
                'contato@contabilidade.com',
                [user.email],
            )
            return render(request, 'usuarios/cadastro_sucesso.html')
        else:
            form = CadastroUsuarioForm()
        return render(request, 'usuarios/cadastro.html', {'form': form})

# A nova view de ativação que você precisa:
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