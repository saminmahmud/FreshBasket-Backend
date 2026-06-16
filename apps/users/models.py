from cloudinary_storage.storage import MediaCloudinaryStorage
from django.db import models
from django_resized import ResizedImageField
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static


class CustomUser(AbstractUser):
    roles = [
        ('customer', 'Customer'),
        ('delivery_partner', 'Delivery Partner'),
        ('admin', 'Admin'),
    ]
    image = ResizedImageField(size=[300, 300], upload_to='avatars/', null=True, blank=True, quality=75, storage=MediaCloudinaryStorage())
    role = models.CharField(max_length=20, choices=roles, default='customer')
    phone = models.CharField(max_length=11, null=True, blank=True)

    def __str__(self):
        return self.username
    
    @property
    def avatar(self):
        try:
            avatar = self.image.url
        except:
            avatar = static('avatars/default_pic.jpg')
        return avatar
    
    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]