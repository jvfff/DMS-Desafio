from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialApp
from autenticacao.models import UserProfile

class RegisterViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.social_app = SocialApp.objects.create(
            provider='google', 
            name='Google', 
            client_id='test-id', 
            secret='test-secret'
        )
        self.social_app.sites.add(1)  

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/registrar.html')

    def test_register_view_post(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_code'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_view_post_invalid(self):
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': 'invalidemail',
            'password1': 'password',
            'password2': 'differentpassword'
        })
        self.assertEqual(response.status_code, 200)  
        self.assertFalse(User.objects.filter(email='invalidemail').exists())
        self.assertTemplateUsed(response, 'autenticacao/registrar.html')

class VerifyCodeViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', email='test@example.com')
        self.profile = UserProfile.objects.create(user=self.user, verification_code='123456')
        self.user.is_active = False
        self.user.save()

        self.social_app = SocialApp.objects.create(
            provider='google', 
            name='Google', 
            client_id='test-id', 
            secret='test-secret'
        )
        self.social_app.sites.add(1)  

    def test_verify_code_view_get(self):
        response = self.client.get(reverse('verify_code'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/verify_code.html')

    def test_verify_code_view_post_valid(self):
        response = self.client.post(reverse('verify_code'), {'code': '123456'})
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_verified)
        self.assertTrue(self.profile.user.is_active)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_verify_code_view_post_invalid(self):
        response = self.client.post(reverse('verify_code'), {'code': 'invalid'})
        self.assertFalse(self.profile.is_verified)
        self.assertFalse(self.profile.user.is_active)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/verify_code.html')

class PasswordResetRequestViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', email='test@example.com')
        self.profile = UserProfile.objects.create(user=self.user)

        self.social_app = SocialApp.objects.create(
            provider='google', 
            name='Google', 
            client_id='test-id', 
            secret='test-secret'
        )
        self.social_app.sites.add(1)  

    def test_password_reset_request_view_get(self):
        response = self.client.get(reverse('password_reset_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/password_reset_request.html')

    def test_password_reset_request_view_post(self):
        response = self.client.post(reverse('password_reset_request'), {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_verify'))
        self.assertTrue(UserProfile.objects.filter(user=self.user, reset_code__isnull=False).exists())

    def test_password_reset_request_view_post_invalid(self):
        response = self.client.post(reverse('password_reset_request'), {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'autenticacao/password_reset_request.html')

class PasswordResetVerifyViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', email='test@example.com')
        self.profile = UserProfile.objects.create(user=self.user, reset_code='123456')

        self.social_app = SocialApp.objects.create(
            provider='google', 
            name='Google', 
            client_id='test-id', 
            secret='test-secret'
        )
        self.social_app.sites.add(1) 

    def test_password_reset_verify_view_get(self):
        response = self.client.get(reverse('password_reset_verify'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/password_reset_verify.html')

    def test_password_reset_verify_view_post_valid(self):
        response = self.client.post(reverse('password_reset_verify'), {'code': '123456'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_complete'))

    def test_password_reset_verify_view_post_invalid(self):
        response = self.client.post(reverse('password_reset_verify'), {'code': 'invalid'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/password_reset_verify.html')

class HomeViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_home_view_get(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')

class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', email='test@example.com')

    def test_logout_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

class PerfilViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', email='test@example.com')
        self.client.login(username='testuser', password='12345')

    def test_perfil_view_get(self):
        response = self.client.get(reverse('perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/perfil.html')

    def test_perfil_view_post(self):
        response = self.client.post(reverse('perfil'), {'field': 'nome', 'value': 'Novo Nome'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('perfil'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.userprofile.nome, 'Novo Nome')