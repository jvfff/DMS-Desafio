from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.core.mail import send_mail, backends
from django.core.mail.backends import smtp
from django.utils.encoding import force_bytes
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os
from dotenv import load_dotenv
import django
from autenticacao.models import Campo, Reserva, Avaliacao, UserProfile
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

class RegisterViewTest(TestCase):
    def test_get_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/registrar.html')

    def test_post_register_view_valid_data(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        })
        self.assertRedirects(response, reverse('verify_code'))
        self.assertIn('verification_code', self.client.session)
        self.assertIn('user_data', self.client.session)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Código de Verificação', mail.outbox[0].subject)

    def test_post_register_view_invalid_data(self):
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': 'invalid-email',
            'password1': 'test',
            'password2': 'test',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/registrar.html')

class VerifyCodeViewTest(TestCase):
    def setUp(self):
        self.session = self.client.session
        self.session['verification_code'] = '123456'
        self.session['user_data'] = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123',
        }
        self.session.save()

    def test_get_verify_code_view(self):
        response = self.client.get(reverse('verify_code'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/verify_code.html')

    def test_post_verify_code_view_valid_code(self):
        response = self.client.post(reverse('verify_code'), {'code': '123456'})
        self.assertRedirects(response, reverse('home'))
        user = User.objects.get(username='testuser')
        self.assertTrue(user.is_authenticated)

    def test_post_verify_code_view_invalid_code(self):
        response = self.client.post(reverse('verify_code'), {'code': '654321'})
        self.assertEqual(response.status_code, 200)

class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='TestPassword123', email='test@example.com')
        self.user.is_active = True
        self.user.save()
        
        social_app = SocialApp.objects.create(provider='google', name='Google', client_id='fake-id', secret='fake-secret')
        social_app.sites.add(Site.objects.get_current())

    def test_get_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/login.html')

    def test_post_login_view_valid_data(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPassword123',
        })
        self.assertRedirects(response, reverse('verify_code_login'))
        self.assertIn('verification_code', self.client.session)
        self.assertIn('username', self.client.session)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Código de Verificação para Login', mail.outbox[0].subject)

    def test_post_login_view_invalid_data(self):
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/login.html')

class VerifyCodeLoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='TestPassword123', email='test@example.com')
        self.user.is_active = True
        self.user.save()

        self.session = self.client.session
        self.session['verification_code'] = '123456'
        self.session['username'] = 'testuser'
        self.session.save()

    def test_get_verify_code_login_view(self):
        response = self.client.get(reverse('verify_code_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/verify_code.html')

    def test_post_verify_code_login_view_valid_code(self):
        response = self.client.post(reverse('verify_code_login'), {'code': '123456'})
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(self.user.is_authenticated)

    def test_post_verify_code_login_view_invalid_code(self):
        response = self.client.post(reverse('verify_code_login'), {'code': '654321'})
        self.assertEqual(response.status_code, 200)

from django.test.utils import override_settings

class PasswordResetRequestViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='TestPassword123')

    def test_get_password_reset_request_view(self):
        response = self.client.get(reverse('password_reset_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/password_reset_request.html')

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    )
    def test_post_password_reset_request_view_valid_email(self):
        response = self.client.post(reverse('password_reset_request'), {'email': 'test@example.com'})

        self.assertEqual(len(mail.outbox), 1)

    def test_post_password_reset_request_view_invalid_email(self):
        response = self.client.post(reverse('password_reset_request'), {'email': 'invalid@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email não encontrado.')

from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

class ActivateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='TestPassword123')
        self.user.is_active = True
        self.user.save()

    def test_activate_view_valid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': token}))
        self.assertRedirects(response, reverse('home'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_view_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': 'invalid-token'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/activation_invalid.html')

class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='TestPassword123', email='test@example.com')
        self.client.login(username='testuser', password='TestPassword123')

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse('_auth_user_id' in self.client.session)

"""
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
"""

class AutenticacaoTests(TestCase):

    def setUp(self):
        image_content = b'\x00\x01\x02'  
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_content,
            content_type='image/jpeg'
        )

        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_profile = UserProfile.objects.create(user=self.user)

        self.user2 = User.objects.create_user(username='otheruser', password='12345')

        self.campo = Campo.objects.create(
            nome='Campo Teste',
            localizacao='Teste City',
            preco_por_hora=50,
            preco_por_dia=400,
            usuario=self.user,
            vestiarios=4,
            iluminacao=True,
            tipo_gramado='natural',
            status='aprovado',
            fotos=image_file  
        )

        self.reserva = Reserva.objects.create(
            campo=self.campo, usuario=self.user, data=timezone.now(),
            tipo_reserva='dia', valor_total=400, status='pendente'
        )

        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def test_pesquisa_campos(self):
        response = self.client.get(reverse('pesquisa_campos'), {'q': 'Campo Teste'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Campo Teste')

    def test_detalhes_campo(self):
        response = self.client.get(reverse('detalhes_campo', args=[self.campo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Campo Teste')

    def test_aprovar_reserva(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('aprovar_reserva', args=[self.reserva.id]))
        self.reserva.refresh_from_db()
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(self.reserva.status, 'aprovado')

    def test_recusar_reserva(self):
        response = self.client.post(reverse('recusar_reserva', args=[self.reserva.id]))
        self.reserva.refresh_from_db()
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(self.reserva.status, 'recusado')

    def test_meus_pedidos(self):
        response = self.client.get(reverse('meus_pedidos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Campo Teste')

    def test_pedidos_recebidos(self):
        response = self.client.get(reverse('pedidos_recebidos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Campo Teste')

    def test_reserva_detalhes(self):
        data = {
            'campo': self.campo.id,
            'data': timezone.now().strftime('%Y-%m-%d'),  
            'tipo_reserva': 'dia',
        }
        response = self.client.post(reverse('detalhes_campo', args=[self.campo.id]), data)

        if response.status_code == 200:
            print(response.context['form'].errors)  

        self.assertEqual(response.status_code, 302)  


    def test_avaliar_campo(self):
        data = {'nota': 5, 'comentario': 'Excelente campo!', 'estrelas': 5}  
        response = self.client.post(reverse('avaliar_campo', args=[self.campo.id]), data)
        
        if response.status_code == 200:
            print(response.context['form'].errors)  

        self.assertEqual(response.status_code, 302)


    def test_campo_detalhes(self):
        response = self.client.get(reverse('info_campo', args=[self.campo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Campo Teste')

    def test_lista_campos_aprovados(self):
        response = self.client.get(reverse('lista_campos_aprovados'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Campo Teste')

"""
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
"""

class AutenticacaoTests(TestCase):
    
    def setUp(self):
        image_content = b'\x00\x01\x02'  
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_content,
            content_type='image/jpeg'
        )

        self.user = User.objects.create_user(username='testuser', password='12345', email='testuser@example.com')
        self.user_profile = UserProfile.objects.create(user=self.user)

        self.campo = Campo.objects.create(
            nome='Campo Teste',
            localizacao='Teste City',
            preco_por_hora=50,
            preco_por_dia=400,
            usuario=self.user,
            vestiarios=4,
            iluminacao=True,
            tipo_gramado='natural',
            status='pendente',
            fotos=image_file
        )

        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def test_aprovar_campo(self):
        admin = User.objects.create_superuser(username='adminuser', password='adminpass', email='admin@example.com')
        self.client.login(username='adminuser', password='adminpass')

        response = self.client.post(reverse('aprovar_campo', args=[self.campo.id]))

        self.campo.refresh_from_db()
        self.assertEqual(self.campo.status, 'aprovado')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.campo.nome, mail.outbox[0].subject)
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_password_reset_request(self):
        response = self.client.post(reverse('password_reset_request'), {'email': self.user.email})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Código de Redefinição de Senha', mail.outbox[0].subject)
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_password_reset_complete(self):
        self.user_profile.reset_code = '123456'
        self.user_profile.save()

        self.client.post(reverse('password_reset_verify'), {'code': '123456'})

        data = {
            'new_password1': 'newpassword@123',
            'new_password2': 'newpassword@123',
        }
        response = self.client.post(reverse('password_reset_complete'), data)

        if response.status_code == 200:
            print(response.context['form'].errors)  

        self.assertEqual(response.status_code, 302)


    def test_register_view(self):
        self.client.logout()
        data = {
            'username': 'newuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'newuser@example.com'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_code'))

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Código de Verificação', mail.outbox[0].subject)
        self.assertIn('newuser@example.com', mail.outbox[0].to)

    def test_login_view(self):
        data = {
            'username': 'testuser',
            'password': '12345',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_code_login'))

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Código de Verificação para Login', mail.outbox[0].subject)
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_verify_code_view(self):
        session = self.client.session
        session['user_data'] = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpassword',
        }
        session['verification_code'] = '123456'
        session.save()

        response = self.client.post(reverse('verify_code'), {'code': '123456'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        user = User.objects.get(username='newuser')
        self.assertIsNotNone(user)
        self.assertTrue(user.is_active)

    def test_gerar_relatorio_pdf(self):
        response = self.client.get(reverse('gerar_relatorio_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_gerar_relatorio_pdf_campo(self):
        response = self.client.get(reverse('gerar_relatorio_pdf_campo', args=[self.campo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_gerar_relatorio_csv(self):
        response = self.client.get(reverse('gerar_relatorio_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_gerar_relatorio_csv_campo(self):
        response = self.client.get(reverse('gerar_relatorio_csv_campo', args=[self.campo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

"""
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------
"""

class ActivateViewTestInvalidToken(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='TestPassword123')
        self.user.is_active = False
        self.user.save()

    def test_activate_view_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        invalid_token = 'invalid-token'
        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': invalid_token}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'autenticacao/activation_invalid.html')

class ReservaViewTestInvalidData(TestCase):
    def setUp(self):
        image_content = b'\x00\x01\x02'  
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_content,
            content_type='image/jpeg'
        )

        self.user = User.objects.create_user(username='testuser', password='12345')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            localizacao='Teste City',
            preco_por_hora=50,
            preco_por_dia=400,
            usuario=self.user,
            vestiarios=4,
            iluminacao=True,
            tipo_gramado='natural',
            status='aprovado',
            fotos=image_file 
        )
        self.client.login(username='testuser', password='12345')

    def test_reserva_com_dados_invalidos(self):
        response = self.client.post(reverse('detalhes_campo', args=[self.campo.id]), {})
        self.assertEqual(response.status_code, 200)

class GerarRelatorioViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            localizacao='Teste City',
            preco_por_hora=50,
            preco_por_dia=400,
            usuario=self.user,
            vestiarios=4,  
            iluminacao=True,
            tipo_gramado='natural',
            status='aprovado'
        )

        self.client.login(username='testuser', password='12345')

    def test_gerar_relatorio_pdf_sem_reservas(self):
        response = self.client.get(reverse('gerar_relatorio_pdf_campo', args=[self.campo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_gerar_relatorio_csv_sem_reservas(self):
        response = self.client.get(reverse('gerar_relatorio_csv_campo', args=[self.campo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

class PermissionsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.admin = User.objects.create_superuser(username='adminuser', password='adminpass', email='admin@example.com')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            localizacao='Teste City',
            preco_por_hora=50,
            preco_por_dia=400,
            usuario=self.user,
            vestiarios=4,
            iluminacao=True,
            tipo_gramado='natural',
            status='pendente'
        )
        self.client = Client()



    def test_admin_aprova_campo(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(reverse('aprovar_campo', args=[self.campo.id]))
        self.assertEqual(response.status_code, 302)
        self.campo.refresh_from_db()
        self.assertEqual(self.campo.status, 'aprovado')

class PasswordResetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', email='testuser@example.com')
        self.user_profile = UserProfile.objects.create(user=self.user, reset_code='123456')

    def test_resetar_senha_com_codigo_invalido(self):
        response = self.client.post(reverse('password_reset_verify'), {'code': '654321'})
        self.assertEqual(response.status_code, 200)



    def test_resetar_senha_com_sucesso(self):
        data = {'code': '123456'}
        response = self.client.post(reverse('password_reset_verify'), data)
        self.assertRedirects(response, reverse('password_reset_complete'))

class CustomUserCreationFormTest(TestCase):
    def test_form_com_dados_invalidos(self):
        response = self.client.post(reverse('register'), {
            'username': '',  
            'email': 'email@invalido',  
            'password1': '123',  
            'password2': '321'
        })
        
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Este campo é obrigatório')
        self.assertContains(response, 'Informe um endereço de email válido.')


        self.assertContains(response, 'Os dois campos de senha não correspondem.')


    def test_form_com_sucesso(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123'
        })
        self.assertRedirects(response, reverse('verify_code'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Código de Verificação', mail.outbox[0].subject)