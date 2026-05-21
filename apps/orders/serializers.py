from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Order, OrderItem, DeliveryCharge, Address
from apps.users.serializers import UserMiniSerializer
from .utils import generate_transaction_id
from apps.products.models import Product


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


class OrderSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    items = OrderItemSerializer(many=True)
    delivery_charge = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'full_name', 'phone', 'address', 'city', 'postal_code',
            'delivery_partner', 'payment_method', 'order_status', 'subtotal', 'total_price', 'tracking_code',
            'is_paid', 'otp', 'is_otp_verified', 'delivery_area', 'delivery_charge',
            'created_at', 'items'
        ]
        read_only_fields = ['user', 'subtotal', 'total_price', 'is_paid', 'otp', 'is_otp_verified', 'delivery_charge', 'created_at']

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
        order.tracking_code = f"TRK{generate_transaction_id()}"

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
    class Meta:
        model = DeliveryCharge
        fields = ['id', 'delivery_area', 'charge_amount']


class OTPVerificationSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    otp = serializers.CharField(max_length=6)


class OrderTrackingSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'full_name', 'phone', 'address', 'city', 'postal_code',
            'delivery_partner', 'payment_method', 'order_status',
            'transaction_id', 'tracking_code',
            'created_at', 'subtotal', 'delivery_charge', 'total_price',
            'is_otp_verified', 'otp', 'delivery_area', 'items'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'created_at', 'tracking_code',
            'subtotal', 'delivery_charge', 'total_price', 'items'
        ]

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_price(self, obj):
        return obj.total_price
    
    
