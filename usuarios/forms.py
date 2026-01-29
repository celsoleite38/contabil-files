from django import forms
from .models import Usuario

class CadastroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'empresa', 'tipo', 'setor']
        

    def clean(self):
        cleaned_data = super().clean()
        empresa = cleaned_data.get('empresa')
        tipo = cleaned_data.get('tipo')

        if tipo == 'CLIENTE' and empresa:
            # Se for edição, precisamos excluir o usuário atual da contagem
            usuarios_qs = Usuario.objects.filter(empresa=empresa)
            if self.instance.pk:
                usuarios_qs = usuarios_qs.exclude(pk=self.instance.pk)
            
            total = usuarios_qs.count()
            
            if total >= empresa.limite_usuarios:
                # Vincula o erro diretamente ao campo 'empresa'
                self.add_error('empresa', f"Limite de {empresa.limite_usuarios} usuários atingido para esta empresa.")
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
    
class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'tipo', 'empresa', 'setor']
        labels = {
            'first_name': 'Nome Completo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'