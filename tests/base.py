from uuid import uuid4
from django.test import TestCase
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

User = get_user_model()


class BaseTestCase(TestCase):
    
    def create_user(self, username="test", email=None, password="Password123@", verified=True, **kwargs):
        if email is None:
            email = f"{username}-{uuid4().hex[:8]}@example.com"
        user =  User.objects.create_user(username=username, email=email, password=password, **kwargs)
        
        EmailAddress.objects.create(user=user, email=email, verified=verified, primary=True)
        
        return user
    
    