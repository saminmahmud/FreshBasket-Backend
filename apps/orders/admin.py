from django.contrib import admin
from .models import Address, DeliveryCharge, Order, OrderItem, DeliveryPartnerProfile, OrderLiveLocation
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'address', 'city', 'postal_code')
    search_fields = ('user__username', 'full_name', 'phone', 'address', 'city', 'postal_code')


@admin.register(DeliveryCharge)
class DeliveryChargeAdmin(admin.ModelAdmin):
    list_display = ('delivery_area', 'charge_amount')
    search_fields = ('delivery_area',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'city', 'postal_code', 'payment_method', 'order_status', 'created_at')
    search_fields = ('user__username', 'full_name', 'phone', 'city', 'postal_code')
    list_filter = ('order_status', 'payment_method')
    inlines = [OrderItemInline]


@admin.register(DeliveryPartnerProfile)
class DeliveryPartnerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'vehicle_type')
    search_fields = ('user__username',)
    
@admin.register(OrderLiveLocation)
class OrderLiveLocationAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_partner', 'latitude', 'longitude', 'updated_at')
    search_fields = ('order__id', 'delivery_partner__user__username')