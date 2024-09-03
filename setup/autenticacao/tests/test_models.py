from django.test import TestCase
from django.contrib.auth.models import User
from autenticacao.models import UserProfile, Campo, Reserva

class UserProfileModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
    
    def test_userprofile_creation(self):
        user_profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(user_profile.user.username, 'testuser')
        self.assertFalse(user_profile.is_verified)
        self.assertEqual(str(user_profile), 'testuser')

class CampoModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
    
    def test_campo_creation(self):
        campo = Campo.objects.create(
            nome='Campo Teste',
            localizacao='Local Teste',
            usuario=self.user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=2,
            largura=30.00,
            comprimento=50.00,
            capacidade=100,
            preco_por_hora=100.00
        )
        self.assertEqual(str(campo), 'Campo Teste')

class ReservaModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            localizacao='Local Teste',
            usuario=self.user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=2,
            largura=30.00,
            comprimento=50.00,
            capacidade=100,
            preco_por_hora=100.00
        )

    def test_reserva_creation(self):
        reserva = Reserva.objects.create(
            campo=self.campo,
            usuario=self.user,
            data='2024-08-20',
            tipo_reserva='hora',
            hora_inicio='10:00',
            hora_fim='12:00',
            valor_total=200.00
        )
        self.assertEqual(str(reserva), 'testuser - Campo Teste em 2024-08-20 das 10:00 às 12:00') 
