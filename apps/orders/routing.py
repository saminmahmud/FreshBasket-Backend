from django.urls import re_path
from .consumers import OrderLiveLocationConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/orders/(?P<order_id>\d+)/live-location/$", OrderLiveLocationConsumer.as_asgi()),
]