from django.test import TestCase
from django.contrib.auth.models import User
from autenticacao.models import UserProfile

class UserProfileModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', email='test@example.com')

    def test_user_profile_creation(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.user.username, 'testuser')
        self.assertFalse(profile.is_verified)
        self.assertIsNone(profile.verification_code)
        self.assertIsNone(profile.reset_code)
