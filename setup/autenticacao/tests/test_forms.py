from django.test import TestCase
from autenticacao.forms import CustomUserCreationForm, VerificationForm, PasswordResetRequestForm, CampoForm, ReservaForm

class CustomUserCreationFormTest(TestCase):
    
    def test_valid_form(self):
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        })
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)

class VerificationFormTest(TestCase):
    
    def test_valid_verification_form(self):
        form = VerificationForm(data={'code': '123456'})
        self.assertTrue(form.is_valid())
    
    def test_invalid_verification_form(self):
        form = VerificationForm(data={'code': ''})
        self.assertFalse(form.is_valid())

class PasswordResetRequestFormTest(TestCase):
    
    def test_valid_password_reset_request_form(self):
        form = PasswordResetRequestForm(data={'email': 'test@example.com'})
        self.assertTrue(form.is_valid())
    
    def test_invalid_password_reset_request_form(self):
        form = PasswordResetRequestForm(data={'email': ''})
        self.assertFalse(form.is_valid())

class CampoFormTest(TestCase):

    def test_valid_campo_form(self):
        form = CampoForm(data={
            'nome': 'Campo Teste',
            'localizacao': 'Local Teste',
            'tipo_gramado': 'natural',
            'iluminacao': True,
            'vestiarios': 2,
            'largura': 30.00,
            'comprimento': 50.00,
            'capacidade': 100,
            'preco_por_hora': 100.00
        })
        self.assertTrue(form.is_valid())

    def test_invalid_campo_form(self):
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)


class ReservaFormTest(TestCase):
    
    def test_valid_reserva_form(self):
        form = ReservaForm(data={
            'data': '2024-08-20',
            'tipo_reserva': 'hora',
            'hora_inicio': '10:00',
            'hora_fim': '12:00'
        })
        self.assertTrue(form.is_valid())
    
    def test_invalid_reserva_form(self):
        form = ReservaForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
