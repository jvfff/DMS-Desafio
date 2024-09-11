from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile, Campo, Reserva, Avaliacao

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
    code = forms.CharField(max_length=6, min_length=6, required=True)

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

class CampoForm(forms.ModelForm):
    class Meta:
        model = Campo
        fields = ['nome', 'localizacao', 'tipo_gramado', 'iluminacao', 'vestiarios', 'largura', 'comprimento', 
                  'capacidade', 'facilidades', 'fotos', 'preco_por_hora', 'preco_por_dia', 'disponibilidade', 
                  'descricao_adicional', 'dias_disponiveis', 'horarios_disponiveis']

    def __init__(self, *args, **kwargs):
        super(CampoForm, self).__init__(*args, **kwargs)
        self.fields['dias_disponiveis'].widget.attrs.update({'class': 'form-control'})
        self.fields['horarios_disponiveis'].widget.attrs.update({'class': 'form-control'})
        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['localizacao'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_gramado'].widget.attrs.update({'class': 'form-control'})
        self.fields['iluminacao'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['vestiarios'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['largura'].widget.attrs.update({'class': 'form-control'})
        self.fields['comprimento'].widget.attrs.update({'class': 'form-control'})
        self.fields['capacidade'].widget.attrs.update({'class': 'form-control'})
        self.fields['facilidades'].widget.attrs.update({'class': 'form-control'})
        self.fields['fotos'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['preco_por_hora'].widget.attrs.update({'class': 'form-control'})
        self.fields['preco_por_dia'].widget.attrs.update({'class': 'form-control'})
        self.fields['disponibilidade'].widget.attrs.update({'class': 'form-control'})
        self.fields['descricao_adicional'].widget.attrs.update({'class': 'form-control'})

class CampoFilterForm(forms.Form):
    nome = forms.CharField(required=False, label='Nome do Campo')
    localizacao = forms.CharField(required=False, label='Localização')
    tipo_gramado = forms.ChoiceField(choices=[('natural', 'Natural'), ('sintetico', 'Sintético')], required=False)
    iluminacao = forms.BooleanField(required=False, label='Iluminação')
    vestiarios = forms.IntegerField(required=False, label='Vestiários')
    capacidade_minima = forms.IntegerField(required=False, label='Capacidade Mínima')
    preco_minimo = forms.DecimalField(required=False, label='Preço Mínimo (R$)', max_digits=8, decimal_places=2)
    preco_maximo = forms.DecimalField(required=False, label='Preço Máximo (R$)', max_digits=8, decimal_places=2)

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['data', 'tipo_reserva', 'hora_inicio', 'hora_fim']
        widgets = {
            'data': forms.SelectDateWidget(),
            'hora_inicio': forms.TimeInput(format='%H:%M'),
            'hora_fim': forms.TimeInput(format='%H:%M'),
        }
        
    def __init__(self, *args, **kwargs):
        super(ReservaForm, self).__init__(*args, **kwargs)
        self.fields['hora_inicio'].required = False
        self.fields['hora_fim'].required = False

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['estrelas', 'comentario']
        labels = {
            'estrelas': 'Avaliação (1-5 estrelas)',
            'comentario': 'Comentário',
        }
        widgets = {
            'estrelas': forms.RadioSelect(),  
        }