from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

FRONTEND_URL = settings.FRONTEND_URL

@shared_task
def send_order_confirmation_email(tracking_code, user_email):
    subject = 'FreshBasket Order Confirmation'
    message = f'Thank you for your order! Your order tracking code is {tracking_code}. You can track your order at {FRONTEND_URL}/track/order?tracking_id={tracking_code}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)
    
    
@shared_task
def send_order_stock_low_email(product_name, product_id, stock_quantity):
    subject = 'FreshBasket Stock Alert'
    message = f'The stock for the product "{product_name}" (ID: {product_id}) is low. Current stock quantity: {stock_quantity}. Please restock soon.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [settings.EMAIL_HOST_USER]
    send_mail(subject, message, email_from, recipient_list)