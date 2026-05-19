from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static


class CustomUser(AbstractUser):
    image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_delivery_partner = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    @property
    def avatar(self):
        try:
            avatar = self.image.url
        except:
            avatar = static('images/avatar.svg')
        return avatar