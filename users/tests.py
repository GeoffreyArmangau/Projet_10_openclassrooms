from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User

class UserRegistrationTests(APITestCase):
    def test_register_user_success(self):
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