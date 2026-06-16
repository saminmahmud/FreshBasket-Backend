from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth import get_user_model
from apps.orders.models import Address, DeliveryPartnerProfile

User = get_user_model()      
        
@receiver(pre_save, sender=User)
def user_presave(sender, instance, **kwargs):
    if instance.username:
        instance.username = instance.username.lower()

    if not hasattr(instance, 'address'):
        Address.objects.create(user=instance)
    
    if instance.is_superuser:
        instance.role = 'admin'    
        
    if instance.role == 'delivery_partner' and not hasattr(instance, 'delivery_partner_profile'):
        DeliveryPartnerProfile.objects.create(user=instance)
