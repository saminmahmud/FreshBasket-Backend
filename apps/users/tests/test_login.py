from rest_framework import status
from rest_framework.test import APITestCase
from tests.base import BaseTestCase


class LoginAPITestCase(BaseTestCase, APITestCase):
    def setUp(self):
        self.url = "/api/auth/login/"
        
        self.user = self.create_user(
            username="test",
            email="test@example.com",
            password="password123"
        )
        
    def test_login_with_email(self):
        response = self.client.post(
            self.url,
            data={
                'login': self.user.email,
                'password': 'password123'
            },
            format='json'
        )
        
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        
    def test_login_with_username(self):
        response = self.client.post(
            self.url,
            data={
                'login': self.user.username,
                'password': 'password123'
            },
            format='json'
        )
        
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        
    def test_login_jwt_response_structure(self):
        response = self.client.post(
            self.url,
            data={
                'login': self.user.email,
                'password': 'password123'
            },
            format='json'
        )
        
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    