from django.test import TestCase
from autenticacao.forms import CustomUserCreationForm

class CustomUserCreationFormTest(TestCase):

    def test_valid_form(self):
        form = CustomUserCreationForm({
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        })
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = CustomUserCreationForm({
            'username': 'testuser',
            'email': 'invalidemail',
            'password1': 'password',
            'password2': 'differentpassword'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)
