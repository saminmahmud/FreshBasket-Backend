from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.serializers import UserDetailsSerializer
from drf_spectacular.utils import extend_schema_field

User = get_user_model()


class CustomUserDetailsSerializer(UserDetailsSerializer):
    is_admin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'is_delivery_partner', 'is_admin')

    @extend_schema_field(serializers.BooleanField)
    def get_is_admin(self, user):
        return user.is_staff


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "avatar",
            "is_delivery_partner",
            "is_admin",
        ]

    @extend_schema_field(serializers.CharField)
    def get_avatar(self, user):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(user.avatar)
        else:
            return user.avatar
        
    @extend_schema_field(serializers.BooleanField)
    def get_is_admin(self, user):
        return user.is_staff
        

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
        if request:
            return request.build_absolute_uri(user.avatar)
        else:
            return user.avatar