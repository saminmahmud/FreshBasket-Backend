from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class RegistrationAPITestCase(APITestCase):
    def setUp(self):
        self.url = "/api/auth/registration/"
        
        self.valid_payload = {
            'username': 'test',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        
    def test_registration_with_valid_data(self):
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertTrue(User.objects.filter(email=self.valid_payload['email']).exists())
        
        user = User.objects.get(email=self.valid_payload['email'])
        
        self.assertEqual(
            user.username,
            "test"
        )
        
    def test_registration_with_duplicate_email(self):
        self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )
        
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_registration_with_weak_password(self):
        payload = self.valid_payload.copy()
        payload['password1'] = '123'
        payload['password2'] = '123'
        
        response = self.client.post(
            self.url,
            data=payload,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
      
    def test_verification_email_is_sent(self):
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )
          
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(response.data['detail'], 'Verification e-mail sent.')
        
        