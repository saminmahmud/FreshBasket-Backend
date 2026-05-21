from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import * 

router = DefaultRouter()

router.register('address', AddressViewSet, basename='address')
router.register('delivery-charges', DeliveryChargeViewSet, basename='delivery-charge')
router.register('orders', OrderViewSet, basename='order')


urlpatterns = [
    path("", include(router.urls)),
    path('otp-verify/', OTPVerificationAPIView.as_view(), name='otp-verify'),
    path('order-status-update/<int:order_id>/', OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
    path('orders/payment/purchase/<int:order_id>/<str:tran_id>/', Purchase, name='purchase'),
    path('orders/payment/cancle-or-fail/<int:order_id>/', Cancle_or_Fail, name='cancle-or-fail'),
    path('orders/tracking/<str:tracking_code>/', OrderTrackingAPIView.as_view(), name='order-tracking'),
]