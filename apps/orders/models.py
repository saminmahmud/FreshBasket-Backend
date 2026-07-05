from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product

User = get_user_model()


class DeliveryCharge(models.Model):
    DELIVERY_AREA_CHOICES = [
        ('inside_dhaka', 'Inside Dhaka'),
        ('outside_dhaka', 'Outside Dhaka'),
    ]
    delivery_area = models.CharField(max_length=20, choices=DELIVERY_AREA_CHOICES, unique=True)
    charge_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_delivery_area_display()} - {self.charge_amount}"
    
    class Meta:
        indexes = [
            models.Index(fields=['delivery_area']),
        ]
        unique_together = ('delivery_area',)
    

class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='address')
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.address}, {self.city}"
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

class DeliveryPartnerProfile(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('bike', 'Bike'),
        ('car', 'Car'),
        ('cycle', 'Cycle'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_partner_profile')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='other', null=True, blank=True)
    vehicle_number = models.CharField(max_length=50, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('ssl_commerz', 'SSL Commerz'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]

    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('assigned_to_delivery', 'Assigned to Delivery'),
        ('packed', 'Packed'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    note = models.TextField(null=True, blank=True)

    delivery_partner = models.ForeignKey(
        DeliveryPartnerProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    tracking_code = models.CharField(max_length=100, null=True, blank=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_otp_verified = models.BooleanField(default=False)
    delivery_area = models.CharField(max_length=20, choices=DeliveryCharge.DELIVERY_AREA_CHOICES)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['order_status']),
            models.Index(fields=['order_status', 'is_otp_verified']),
        ]

    @property
    def total_price(self):
        return self.subtotal + self.delivery_charge
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Order #{self.order.id}"
    
    class Meta:
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]


from django.db import models


class OrderLiveLocation(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="live_location"
    )
    delivery_partner = models.ForeignKey(
        DeliveryPartnerProfile,
        on_delete=models.CASCADE,
        related_name="live_locations"
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["delivery_partner"]),
            models.Index(fields=["updated_at"]),
        ]

    def __str__(self):
        return f"Order #{self.order.id}"