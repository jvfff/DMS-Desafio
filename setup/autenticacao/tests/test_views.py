from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from autenticacao.models import UserProfile, Campo
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

class ViewTests(TestCase):
    
    def setUp(self):
        # Configura o SocialApp necessário para os testes
        site = Site.objects.get_current()
        self.social_app = SocialApp.objects.create(
            provider='google', 
            name='Google', 
            client_id='123', 
            secret='ABC'
        )
        self.social_app.sites.add(site)

        # Configura o cliente de teste e cria um usuário
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', email='testuser@example.com')
        self.user_profile = UserProfile.objects.create(user=self.user, is_verified=True)
        self.campo = Campo.objects.create(
            nome='Campo de Teste',
            localizacao='Local de Teste',
            usuario=self.user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=2,
            largura=30.00,
            comprimento=50.00,
            capacidade=100,
            preco_por_hora=100.00
        )
    
    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/registrar.html')
    
    def test_register_view_post(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Str0ngP@ssword123',
            'password2': 'Str0ngP@ssword123'
        }
        response = self.client.post(reverse('register'), data)
        
        if response.status_code == 200:
            form = response.context.get('form', None)
            if form and form.errors:
                print(form.errors)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_code'))
    
    def test_register_view_post_invalid_email(self):
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'Str0ngP@ssword123',
            'password2': 'Str0ngP@ssword123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('email', form.errors)

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/login.html')
    
    def test_login_view_post(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')
    
    def test_logout_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_cadastrar_campo_view(self):
        self.client.login(username='testuser', password='12345')
        data = {
            'nome': 'Novo Campo',
            'localizacao': 'Novo Local',
            'tipo_gramado': 'natural',
            'iluminacao': True,
            'vestiarios': 3,
            'largura': 40.00,
            'comprimento': 60.00,
            'capacidade': 120,
            'preco_por_hora': 150.00
        }
        response = self.client.post(reverse('cadastrar_campo'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gerenciar_campos'))

    def test_editar_campo_view(self):
        self.client.login(username='testuser', password='12345')
        campo_id = self.campo.id
        data = {
            'nome': 'Campo Editado',
            'localizacao': 'Local Editado',
            'tipo_gramado': 'sintetico',
            'iluminacao': False,
            'vestiarios': 5,
            'largura': 35.00,
            'comprimento': 55.00,
            'capacidade': 150,
            'preco_por_hora': 120.00
        }
        response = self.client.post(reverse('editar_campo', args=[campo_id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gerenciar_campos'))
        self.campo.refresh_from_db()
        self.assertEqual(self.campo.nome, 'Campo Editado')

    def test_editar_campo_view_nonexistent(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('editar_campo', args=[999]))  
        self.assertEqual(response.status_code, 404)

    def test_register_view_post_mismatched_passwords(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Str0ngP@ssword123',
            'password2': 'DifferentP@ssword123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('password2', form.errors)

    def test_meus_pedidos_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('meus_pedidos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/meus_pedidos.html')

    def test_deletar_campo_view(self):
        self.client.login(username='testuser', password='12345')
        campo_id = self.campo.id
        response = self.client.post(reverse('deletar_campo', args=[campo_id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gerenciar_campos'))
        with self.assertRaises(Campo.DoesNotExist):
            Campo.objects.get(id=campo_id)

    def test_admin_gerenciar_campos_access_denied_for_non_admin(self):
        non_admin_user = User.objects.create_user(username='nonadmin', password='12345')
        self.client.login(username='nonadmin', password='12345')
        response = self.client.get(reverse('admin_gerenciar_campos'))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('admin_gerenciar_campos'))

    def test_aprovar_campo_view(self):
        self.client.login(username='testuser', password='12345')
        self.user.is_superuser = True
        self.user.save()
        campo = Campo.objects.create(
            nome='Campo Pendente',
            localizacao='Local Pendente',
            usuario=self.user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=3,
            largura=40.00,
            comprimento=60.00,
            capacidade=120,
            preco_por_hora=150.00,
            status='pendente'
        )
        response = self.client.post(reverse('aprovar_campo', args=[campo.id]))
        self.assertEqual(response.status_code, 302)
        campo.refresh_from_db()
        self.assertEqual(campo.status, 'aprovado')

    def test_recusar_campo_view(self):
        self.client.login(username='testuser', password='12345')
        self.user.is_superuser = True
        self.user.save()
        campo = Campo.objects.create(
            nome='Campo Pendente',
            localizacao='Local Pendente',
            usuario=self.user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=3,
            largura=40.00,
            comprimento=60.00,
            capacidade=120,
            preco_por_hora=150.00,
            status='pendente'
        )
        response = self.client.post(reverse('recusar_campo', args=[campo.id]))
        self.assertEqual(response.status_code, 302)
        campo.refresh_from_db()
        self.assertEqual(campo.status, 'recusado')

    def test_aprovar_campo_view_access_denied_for_non_admin(self):
        non_admin_user = User.objects.create_user(username='nonadmin', password='12345')
        self.client.login(username='nonadmin', password='12345')
        campo = Campo.objects.create(
            nome='Campo Pendente',
            localizacao='Local Pendente',
            usuario=non_admin_user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=3,
            largura=40.00,
            comprimento=60.00,
            capacidade=120,
            preco_por_hora=150.00,
            status='pendente'
        )
        response = self.client.post(reverse('aprovar_campo', args=[campo.id]))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('admin_gerenciar_campos'), fetch_redirect_response=False)
        campo.refresh_from_db()
        self.assertEqual(campo.status, 'pendente')

    def test_password_reset_request_view(self):
        response = self.client.post(reverse('password_reset_request'), {'email': self.user.email})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_verify'))

    def test_password_reset_verify_view(self):
        self.user_profile.reset_code = '123456'
        self.user_profile.save()
        response = self.client.post(reverse('password_reset_verify'), {'code': '123456'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_complete'))

    def test_password_reset_complete_view(self):
        self.user_profile.reset_code = '123456'
        self.user_profile.save()
        response = self.client.post(reverse('password_reset_complete'), {
            'new_password1': 'Str0ngP@ssword123',
            'new_password2': 'Str0ngP@ssword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

