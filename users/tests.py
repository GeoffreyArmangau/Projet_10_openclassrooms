from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User


class UserRegistrationTests(APITestCase):
    """Tests fonctionnels pour l'API d'inscription des utilisateurs."""

    def test_register_user_success(self):
        """
        Vérifie qu'un utilisateur majeur (15 ans et plus) peut s'inscrire.

        Attend une réponse HTTP 201 et la présence de l'utilisateur en base.
        """
        url = reverse('user-register')
        data = {
            'username': 'testolduser',
            'password': 'testpass123',
            'email': 'test@example.com',
            'age': 20,
            'can_be_contacted': True,
            'can_data_be_shared': False
        }
        response = self.client.post(url, data)
        print('Réponse inscription:', response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testolduser').exists())

    def test_register_user_under_15(self):
        """
        Vérifie qu'un utilisateur de moins de 15 ans ne peut pas s'inscrire.

        Attend une réponse HTTP 400 avec une erreur sur le champ `age`,
        conformément aux exigences RGPD de consentement.
        """
        url = reverse('user-register')
        data = {
            'username': 'testyounguser',
            'password': 'testpass123',
            'email': 'young@example.com',
            'age': 12,
            'can_be_contacted': True,
            'can_data_be_shared': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', response.data)
