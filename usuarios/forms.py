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
            total = Usuario.objects.filter(empresa=empresa).count()
            if total >= empresa.limite_usuarios:
                raise forms.ValidationError(f"Limite de {empresa.limite_usuarios} usuários atingido para esta empresa.")
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'tipo', 'empresa', 'setor']