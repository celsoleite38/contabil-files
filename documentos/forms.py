from django import forms
from .models import PedidoDocumento, Empresa, Setor, AgendamentoPedido
from usuarios.models import Usuario

class CriarPedidoForm(forms.ModelForm):
    # Campo para o contador escolher qual usuário da empresa vai receber o e-mail
    usuario_destinatario = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(tipo='CLIENTE'),
        label="Enviar aviso para o usuário"
    )

    class Meta:
        model = PedidoDocumento
        fields = ['titulo', 'descricao_solicitacao', 'empresa_destino', 'setor_solicitante']

class ResponderPedidoForm(forms.ModelForm):
    class Meta:
        model = PedidoDocumento
        fields = ['arquivo_enviado']
        

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome_fantasia', 'cnpj', 'limite_usuarios']
        widgets = {
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'limite_usuarios': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AgendamentoPedidoForm(forms.ModelForm):
    class Meta:
        model = AgendamentoPedido
        fields = ['titulo', 'descricao', 'usuario_destinatario', 'data_agendada', 'repeticao']
        widgets = {
            'data_agendada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Guia de FGTS Mensal'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'usuario_destinatario': forms.Select(attrs={'class': 'form-select'}),
            'repeticao': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'usuario_destinatario': 'Cliente (Destinatário)',
            'data_agendada': 'Data da Primeira Solicitação',
            'repeticao': 'Frequência de Repetição',
        }