from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model
from apps.orders.models import Address, DeliveryPartnerProfile

User = get_user_model()      
        
@receiver(pre_save, sender=User)
def user_presave(sender, instance, **kwargs):
    if not instance.username:
        base = instance.email.split("@")[0].lower()
        username = base
        count = 1

        while User.objects.filter(username=username).exclude(pk=instance.pk).exists():
            username = f"{base}{count}"
            count += 1

        instance.username = username

    if instance.is_superuser:
        instance.role = 'admin'    


@receiver(post_save, sender=User)
def user_postsave(sender, instance, created, **kwargs):
    if not created:
        return

    Address.objects.get_or_create(user=instance)

    if instance.role == 'delivery_partner' and not hasattr(instance, 'delivery_partner_profile'):
        DeliveryPartnerProfile.objects.create(user=instance)