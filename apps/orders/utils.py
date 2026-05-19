import random
import time
import requests
from sslcommerz_lib import SSLCOMMERZ
from .models import Order
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

STORE_ID = settings.STORE_ID
STORE_PASSWORD = settings.STORE_PASSWORD
BACKEND_URL = settings.BACKEND_URL


def generate_otp():
    return str(random.randint(100000, 999999))


def generate_transaction_id():
    timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    return f'TX{timestamp}{random_num}'


def create_sslcommerz_session(order_id):
    try:
        order_qs = Order.objects.get(id=order_id, is_paid=False)
        order_total = order_qs.total_price
        
        tran_id = order_qs.transaction_id

        store_settings = {
            'store_id': STORE_ID,  
            'store_pass': STORE_PASSWORD,
            'issandbox': True 
        }
        sslcz = SSLCOMMERZ(store_settings)
        
        post_body = {
            'total_amount': order_total,
            'currency': "BDT",
            'tran_id': tran_id,
            'success_url': f"{BACKEND_URL}api/orders/payment/purchase/{order_id}/{tran_id}/",
            'fail_url': f"{BACKEND_URL}api/orders/payment/cancle-or-fail/{order_id}/",
            'cancel_url': f"{BACKEND_URL}api/orders/payment/cancle-or-fail/{order_id}/",
            'emi_option': 0,
            'cus_name': order_qs.full_name,
            'cus_email': order_qs.user.email,
            'cus_phone': order_qs.phone,
            'cus_add1': order_qs.address,
            'cus_city': order_qs.city,
            'cus_postcode': order_qs.postal_code,
            'cus_country': "Bangladesh",
            'shipping_method': "NO",
            'num_of_item': order_qs.items.count(),
            'product_name': "FreshBasket Products",
            'product_category': "Grocery Products",
            'product_profile': "general"
        }

        # Call SSLCommerz to create a session
        response = sslcz.createSession(post_body)
        return response
    except Exception as e:
        return {'error': str(e)}


def validate_sslcommerz_transaction(val_id):
    url = "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"

    params = {
        "val_id": val_id,
        "store_id": STORE_ID,
        "store_passwd": STORE_PASSWORD,
        "format": "json"
    }

    response = requests.get(url, params=params)
    return response.json()
        