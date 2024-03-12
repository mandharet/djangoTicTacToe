from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.authapp.models import CustomUser
from rest_framework.authtoken.models import Token

class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.data = {"username": "newuser", "password": "newpassword"}

    def test_signup(self):
        url = reverse('signup')
        data = {"username": "newuser", "password": "newpassword"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)
        self.assertTrue('user_id' in response.data)

    def test_login(self):
        url = reverse('user_login')
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('user_id' in response.data)

    def test_logout(self):
        
        url = reverse('user_login')
        
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(url, data, format='json')
        token= response.data['token']
        if token:
            url = reverse('user_logout')
            response = self.client.post(url, HTTP_AUTHORIZATION=f'Token {token}')
    
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, {'message': 'Logout successful'})

    def tearDown(self):
        pass
