from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth import get_user_model
from apps.orders.models import Address

User = get_user_model()      
        
@receiver(pre_save, sender=User)
def user_presave(sender, instance, **kwargs):
    if instance.username:
        instance.username = instance.username.lower()

    if not hasattr(instance, 'address'):
        Address.objects.create(user=instance)
    
    if instance.is_superuser:
        instance.role = 'admin'    