from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth import get_user_model

User = get_user_model()      
        
@receiver(pre_save, sender=User)
def user_presave(sender, instance, **kwargs):
    if instance.username:
        instance.username = instance.username.lower()


@receiver(pre_save, sender=User)
def set_admin_role(sender, instance, **kwargs):
    if instance.is_superuser:
        instance.role = 'admin' 
    