from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.serializers import UserDetailsSerializer

User = get_user_model()


class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'email')


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(read_only=True)
    name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "avatar",
            "info",   
        ]

    def get_avatar(self, user):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(user.avatar)
        else:
            return user.avatar
        

class UserMiniSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(read_only=True)
    name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "avatar",
        ]

    def get_avatar(self, user):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(user.avatar)
        else:
            return user.avatar