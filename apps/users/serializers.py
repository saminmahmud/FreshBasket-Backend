from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth import authenticate
from allauth.account.models import EmailAddress
from drf_spectacular.utils import extend_schema_field
from dj_rest_auth.serializers import LoginSerializer

User = get_user_model()


class CustomUserDetailsSerializer(UserDetailsSerializer):

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'role')


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "avatar",
            "role"
        ]

    @extend_schema_field(serializers.CharField)
    def get_avatar(self, user):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(user.avatar)
        else:
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
        if request:
            return request.build_absolute_uri(user.avatar)
        else:
            return user.avatar
        

class CustomLoginSerializer(LoginSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    login = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')

        if not password:
            raise serializers.ValidationError("Password is required.")
        if not login:
            raise serializers.ValidationError("Must provide username or email.")

        if '@' in login:
            try:
                user_obj = User.objects.get(email__iexact=login)
                attrs['username'] = user_obj.username
                attrs['email'] = login
            except User.DoesNotExist:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            attrs['username'] = login

        request = self.context.get('request')
        user = authenticate(request, username=attrs['username'], password=password)

        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        try:
            email_address = EmailAddress.objects.get(user=user, primary=True)
            if not email_address.verified:
                raise serializers.ValidationError("Email is not verified.")
        except EmailAddress.DoesNotExist:
            pass

        attrs['user'] = user
        return attrs
