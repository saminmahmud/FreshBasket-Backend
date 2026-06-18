from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth import authenticate
from allauth.account.models import EmailAddress
from drf_spectacular.utils import extend_schema_field
from dj_rest_auth.serializers import LoginSerializer
from apps.orders.models import Address, DeliveryPartnerProfile

User = get_user_model()


class CustomUserDetailsSerializer(UserDetailsSerializer):

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'role')


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "avatar",
            "image",
            "role",
        ]
    read_only_fields = ['role', 'username', 'avatar', 'email']

    @extend_schema_field(serializers.CharField)
    def get_avatar(self, user):
        request = self.context.get('request')
        if request and user.image:
            return request.build_absolute_uri(user.image.url)

        return user.avatar
        

class UserMiniSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "avatar",
        ]

    @extend_schema_field(serializers.CharField)
    def get_avatar(self, user):
        request = self.context.get('request')
        if request and user.image:
            return request.build_absolute_uri(user.image.url)

        return user.avatar
        

class UserWithProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "avatar",
            "role",
            "profile",
        ]
    read_only_fields = ['role', 'username', 'avatar', 'email']

    @extend_schema_field(serializers.CharField)
    def get_avatar(self, user):
        request = self.context.get('request')
        if request and user.image:
            return request.build_absolute_uri(user.image.url)

        return user.avatar
        
    def get_profile(self, user):
        if user.role == 'customer' or user.role == 'admin':
            try:
                address = user.address
                return {
                    'id': address.id,
                    'full_name': address.full_name,
                    'phone': address.phone,
                    'address': address.address,
                    'city': address.city,
                    'postal_code': address.postal_code,
                }
            except Address.DoesNotExist:
                return None
        elif user.role == 'delivery_partner':
            try:
                profile = user.delivery_partner_profile
                return {
                    'id': profile.id,
                    'full_name': profile.full_name,
                    'phone': profile.phone,
                    'address': profile.address,
                    'vehicle_type': profile.vehicle_type,
                    'vehicle_number': profile.vehicle_number,
                }
            except DeliveryPartnerProfile.DoesNotExist:
                return None
        return None