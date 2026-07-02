from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Order, OrderItem, DeliveryCharge, Address, DeliveryPartnerProfile
from apps.users.serializers import UserMiniSerializer, UserSerializer
from .utils import generate_track_id
from apps.products.models import Product
from allauth.account.models import EmailAddress


class ProductForOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'image']


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    product = ProductForOrderSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']
        read_only_fields = ['price']


class DeliveryPartnerProfileMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPartnerProfile
        fields = ['id', 'full_name']
        read_only_fields = ['id', 'full_name']


class OrderSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    items = OrderItemSerializer(many=True)
    delivery_charge = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()
    delivery_partner = DeliveryPartnerProfileMiniSerializer(read_only=True)
    delivery_partner_id = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryPartnerProfile.objects.all(),
        source="delivery_partner",
        write_only=True,
        required=False,
        allow_null=True,
    )
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'full_name', 'phone', 'address', 'city', 'postal_code', 'note',
            'delivery_partner', 'delivery_partner_id', 'payment_method', 'order_status', 'subtotal', 'total_price', 'tracking_code',
            'is_paid', 'otp', 'is_otp_verified', 'delivery_area', 'delivery_charge',
            'created_at', 'items', 'updated_at', 'latitude', 'longitude'
        ]
        read_only_fields = ['user', 'subtotal', 'total_price', 'is_paid', 'otp', 'is_otp_verified', 'delivery_charge', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        subtotal = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.final_price * quantity
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            subtotal += price

        order.subtotal = subtotal
        order.tracking_code = generate_track_id()

        area = validated_data.get('delivery_area')
        delivery_charge = DeliveryCharge.objects.filter(delivery_area=area).first()
        
        if delivery_charge:
            order.delivery_charge = delivery_charge.charge_amount
        
        order.save()
        return order

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_price(self, obj):
        return obj.total_price
    

class AddressSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    class Meta:
        model = Address
        fields = ['id', 'user', 'full_name', 'phone', 'address', 'city', 'postal_code']
        read_only_fields = ['user']


class DeliveryChargeSerializer(serializers.ModelSerializer):
    delivery_area_display = serializers.CharField(
        source='get_delivery_area_display',
        read_only=True
    )

    class Meta:
        model = DeliveryCharge
        fields = ['id', 'delivery_area', 'delivery_area_display', 'charge_amount']


class OTPVerificationSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    otp = serializers.CharField(max_length=6)


class DeliveryPartnerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_active = serializers.SerializerMethodField()
    class Meta:
        model = DeliveryPartnerProfile
        fields = ['id', 'user', 'vehicle_type', 'vehicle_number', 'full_name', 'phone', 'is_active']
        read_only_fields = ['user']
        
    def get_is_active(self, obj):
        user = obj.user
        email_address = EmailAddress.objects.filter(user=user, email=user.email).first()
        if email_address:
            return email_address.verified
        return False


class OrderTrackingSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_partner = DeliveryPartnerProfileSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'full_name', 'phone', 'address', 'city', 'postal_code', 'note',
            'delivery_partner', 'payment_method', 'order_status',
            'transaction_id', 'tracking_code', 'updated_at',
            'created_at', 'subtotal', 'delivery_charge', 'total_price',
            'is_otp_verified', 'otp', 'delivery_area', 'items', 'latitude', 'longitude'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'created_at', 'updated_at', 'tracking_code',
            'subtotal', 'delivery_charge', 'total_price', 'items'
        ]

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_price(self, obj):
        return obj.total_price
    

class AdminDashboardSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_out_of_stock_products = serializers.IntegerField()
    recent_orders = OrderSerializer(many=True, read_only=True)
    
    
    
     
