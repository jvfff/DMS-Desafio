from django.test import TestCase
from autenticacao.models import UserProfile, Campo, Reserva, Avaliacao
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfileTest(TestCase):
    def test_user_profile_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        profile = UserProfile.objects.create(user=user, nome='Test User', cpf='123.456.789-00')
        self.assertEqual(str(profile), 'testuser')
        self.assertEqual(profile.nome, 'Test User')
        self.assertEqual(profile.cpf, '123.456.789-00')

class CampoTest(TestCase):
    def test_campo_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        campo = Campo.objects.create(
            nome='Campo Teste',
            localizacao='Teste City',
            usuario=user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=4,
            largura=40,
            comprimento=60,
            capacidade=100,
            preco_por_hora=100.00,
            preco_por_dia=500.00,
        )
        self.assertEqual(str(campo), 'Campo Teste')
        self.assertEqual(campo.tipo_gramado, 'natural')
        self.assertTrue(campo.iluminacao)

class ReservaTest(TestCase):
    def test_reserva_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        campo = Campo.objects.create(
            nome='Campo Teste',
            localizacao='Teste City',
            usuario=user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=4,
            largura=40,
            comprimento=60,
            capacidade=100,
            preco_por_hora=100.00,
            preco_por_dia=500.00,
        )
        reserva = Reserva.objects.create(
            campo=campo,
            usuario=user,
            data=timezone.now(),
            tipo_reserva='hora',
            hora_inicio='09:00',
            hora_fim='11:00',
            valor_total=200.00
        )
        self.assertEqual(str(reserva), f'{user.username} - {campo.nome} em {reserva.data} das {reserva.hora_inicio} às {reserva.hora_fim}')


class AvaliacaoTest(TestCase):
    def test_avaliacao_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        campo = Campo.objects.create(
            nome='Campo Teste',
            localizacao='Teste City',
            usuario=user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=4,
            largura=40,
            comprimento=60,
            capacidade=100,
            preco_por_hora=100.00,
            preco_por_dia=500.00,
        )
        avaliacao = Avaliacao.objects.create(
            campo=campo,
            usuario=user,
            estrelas=5,
            comentario='Ótimo campo!'
        )
        self.assertEqual(str(avaliacao), f'{user.username} - {campo.nome} (5 estrelas)')
