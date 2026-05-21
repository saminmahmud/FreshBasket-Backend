from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from .serializers import OrderSerializer, AddressSerializer, DeliveryChargeSerializer, OTPVerificationSerializer, OrderTrackingSerializer
from .models import Order, Address, DeliveryCharge
from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from apps.users.permissions import IsEmailVerified, IsDeliveryPartner
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponseRedirect
from .utils import create_sslcommerz_session
from rest_framework.permissions import AllowAny
from django.conf import settings
from rest_framework.validators import ValidationError

FRONTEND_URL = settings.FRONTEND_URL


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsEmailVerified]

    def perform_create(self, serializer):
        if Address.objects.filter(user=self.request.user).exists():
            raise ValidationError("You already have an address")
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class DeliveryChargeViewSet(viewsets.ModelViewSet):
    queryset = DeliveryCharge.objects.all()
    serializer_class = DeliveryChargeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        else:
            return [permissions.AllowAny()]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('user', 'delivery_partner').prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsEmailVerified]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)

        if order.payment_method == "cash_on_delivery":
            return Response({
                "message": "Order created successfully (Cash on Delivery)",
                "order_id": order.id
            }, status=status.HTTP_201_CREATED)

        # ssl session create
        response = create_sslcommerz_session(order.id)

        if not response or 'GatewayPageURL' not in response:
            return Response({'error': 'Failed to create SSLCommerz session'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"payment_url": response['GatewayPageURL'], "order_id": order.id}, status=201)


class OTPVerificationAPIView(APIView):
    permission_classes = [IsDeliveryPartner]
    serializer_class = OTPVerificationSerializer

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data['order_id']
        otp = serializer.validated_data['otp']

        try:
            order = Order.objects.get(id=order_id, delivery_partner=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        if order.otp != otp:
            return Response({'error': 'Invalid OTP'}, status=400)
        
        order.is_otp_verified = True
        order.order_status = "delivered"
        order.save()
        return Response({'message': 'OTP verified and order marked as delivered'}, status=200)


class OrderStatusUpdateAPIView(APIView):
    permission_classes = [IsDeliveryPartner | permissions.IsAdminUser]
    serializer_class = None

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        curr_status = order.order_status
        if curr_status == "assigned_to_delivery":
            order.order_status = "packed"
        elif curr_status == "packed":
            order.order_status = "out_for_delivery"
        elif curr_status == "out_for_delivery":
            if not order.is_otp_verified:
                return Response({'error': 'OTP verification required before marking as delivered'}, status=400)
            order.order_status = "delivered"
        else:
            return Response({'error': 'Invalid status transition'}, status=400)
        order.save()
        return Response({"order_id": order.id, "order_status": order.order_status}, status=200)


@extend_schema(request=None, responses={302: None})
@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def Purchase(request, order_id, tran_id):
    order_qs = Order.objects.filter(id=order_id, transaction_id=tran_id, is_paid=False).first()

    if order_qs:
        order_qs.is_paid = True
        order_qs.transaction_id = tran_id
        order_qs.save()
        return HttpResponseRedirect(f'{FRONTEND_URL}/payment?status=success&order_id={order_id}')

    return HttpResponseRedirect(f'{FRONTEND_URL}/payment?status=failed')


@extend_schema(request=None, responses={302: None})
@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def Cancle_or_Fail(request, order_id):
    order_qs = Order.objects.filter(id=order_id, is_paid=False).first()
    
    if order_qs:
        order_qs.delete() 
        return HttpResponseRedirect(f'{FRONTEND_URL}/payment?status=failed')

    return HttpResponseRedirect(f'{FRONTEND_URL}/payment?status=failed')


class OrderTrackingAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = None

    def get(self, request, tracking_code):
        try:
            order = Order.objects.get(tracking_code=tracking_code)
            serializer = OrderTrackingSerializer(order)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"message": "No order found with this tracking code"}, status=status.HTTP_404_NOT_FOUND)
    
        
    