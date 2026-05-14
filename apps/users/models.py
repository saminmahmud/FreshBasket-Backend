from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static


class CustomUser(AbstractUser):
    image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    info = models.TextField(null=True, blank=True) 

    def __str__(self):
        return self.username
    
    @property
    def avatar(self):
        try:
            avatar = self.image.url
        except:
            avatar = static('images/avatar.svg')
        return avatar
    
    @property
    def name(self):
        if self.display_name:
            return self.display_name
        else:
            return self.username