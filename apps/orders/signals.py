from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.orders.utils import generate_otp
from .models import Order


@receiver(pre_save, sender=Order)
def hold_previous_status(sender, instance, **kwargs):
    if instance.pk:
        instance._previous = Order.objects.only(
            "order_status",
            "delivery_partner"
        ).get(pk=instance.id)
    else:
        instance._previous = None


@receiver(pre_save, sender=Order)
def order_status_change_handler(sender, instance, **kwargs):
    if not instance.pk:
        return
    
    previous = getattr(instance, '_previous', None)
    
    if not previous:
        return
    
    previous_status = previous.order_status
    new_status = instance.order_status
    previous_partner = previous.delivery_partner
    new_partner = instance.delivery_partner

    if previous_partner is None and new_partner:
        instance.order_status = "assigned_to_delivery"
        
    if previous_status == 'packed' and new_status == 'out_for_delivery':
        instance.otp = generate_otp()
        