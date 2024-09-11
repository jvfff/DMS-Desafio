from django.test import TestCase
from autenticacao.forms import CustomUserCreationForm, VerificationForm, PasswordResetRequestForm, PasswordResetVerifyForm, PasswordResetCompleteForm, UserProfileForm, CampoForm, ReservaForm, AvaliacaoForm
from autenticacao.models import Campo, Reserva, Avaliacao, UserProfile
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

class CustomUserCreationFormTest(TestCase):
    def test_form_valido(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form_data = {
            'username': '',
            'email': 'emailinvalido',
            'password1': '123',
            'password2': '321',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

class VerificationFormTest(TestCase):
    def test_verificacao_valida(self):
        form = VerificationForm(data={'code': '123456'})
        self.assertTrue(form.is_valid())

    def test_verificacao_invalida(self):
        form = VerificationForm(data={'code': '123'}) 
        self.assertFalse(form.is_valid())

class PasswordResetRequestFormTest(TestCase):
    def test_form_valido(self):
        form = PasswordResetRequestForm(data={'email': 'testuser@example.com'})
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form = PasswordResetRequestForm(data={'email': 'emailinvalido'})
        self.assertFalse(form.is_valid())

class PasswordResetVerifyFormTest(TestCase):
    def test_form_valido(self):
        form = PasswordResetVerifyForm(data={'code': '123456'})
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form = PasswordResetVerifyForm(data={'code': ''})
        self.assertFalse(form.is_valid())

class PasswordResetCompleteFormTest(TestCase):
    def test_form_valido(self):
        user = User.objects.create_user(username='testuser', password='12345')
        form_data = {
            'new_password1': 'senhaSegura123',
            'new_password2': 'senhaSegura123',
        }
        form = PasswordResetCompleteForm(user=user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        user = User.objects.create_user(username='testuser', password='12345')
        form_data = {
            'new_password1': '12345',
            'new_password2': '54321',
        }
        form = PasswordResetCompleteForm(user=user, data=form_data)
        self.assertFalse(form.is_valid())

class UserProfileFormTest(TestCase):
    def test_form_valido(self):
        user = User.objects.create_user(username='testuser', password='12345')
        form_data = {
            'nome': 'Test User',
            'cpf': '123.456.789-00',
            'cep': '12345-678',
            'endereco': 'Rua Teste, 123',
            'email': 'testuser@example.com',
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

class CampoFormTest(TestCase):
    def test_form_valido(self):
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\xff\x00\xff\xff\xff\x00'
                b'\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00'
                b'\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
            ),  
            content_type='image/gif'
        )

        form_data = {
            'nome': 'Campo Teste',
            'localizacao': 'Teste City',
            'tipo_gramado': 'natural',
            'iluminacao': True,
            'vestiarios': 4,
            'largura': 40,
            'comprimento': 60,
            'capacidade': 100,
            'preco_por_hora': 100.00,
            'preco_por_dia': 500.00,
            'dias_disponiveis': 'Segunda, Terça, Quarta',
            'horarios_disponiveis': '08:00-10:00, 14:00-16:00',
            'disponibilidade': 'Sempre disponível',
            'descricao_adicional': 'Campo em ótimo estado',
        }

        form = CampoForm(data=form_data, files={'fotos': image})
        print(form.errors)  
        self.assertTrue(form.is_valid())  

class ReservaFormTest(TestCase):
    def test_form_valido(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        print(form.errors)  
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form_data = {
            'data': '',
            'tipo_reserva': '',
        }
        form = ReservaForm(data=form_data)
        self.assertFalse(form.is_valid())

class AvaliacaoFormTest(TestCase):
    def test_form_valido(self):
        form_data = {
            'estrelas': 5,
            'comentario': 'Ótimo campo!',
        }
        form = AvaliacaoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form_data = {
            'estrelas': 0,
            'comentario': '',
        }
        form = AvaliacaoForm(data=form_data)
        self.assertFalse(form.is_valid())
