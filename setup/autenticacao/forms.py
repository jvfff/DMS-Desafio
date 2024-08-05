from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nome de Usuário',
            'password1': 'Senha',
            'password2': 'Confirmação de Senha',
        }
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }
        error_messages = {
            'username': {
                'required': 'Este campo é obrigatório.',
                'max_length': 'Máximo de 150 caracteres.',
                'invalid': 'Caracteres inválidos. Use apenas letras, números e @/./+/-/_',
            },
            'email': {
                'required': 'Este campo é obrigatório.',
                'invalid': 'Insira um endereço de email válido.',
            },
            'password1': {
                'required': 'Este campo é obrigatório.',
            },
            'password2': {
                'required': 'Este campo é obrigatório.',
                'password_mismatch': 'As senhas não coincidem.',
            },
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

class VerificationForm(forms.Form):
    code = forms.CharField(max_length=6)

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email")

class PasswordResetVerifyForm(forms.Form):
    code = forms.CharField(max_length=6)

class PasswordResetCompleteForm(SetPasswordForm):
    pass

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nome', 'cpf', 'cep', 'endereco', 'email']
