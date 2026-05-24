from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from allauth.account.models import EmailAddress


class IsEmailVerified(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        is_verified = EmailAddress.objects.filter(
            user=request.user,
            email=request.user.email,
            verified=True
        ).exists()

        if not is_verified:
            raise PermissionDenied({
                "error": "EMAIL_NOT_VERIFIED",
                "message": "Please verify your email before accessing this resource."
            })

        return True
    

class IsDeliveryPartner(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not request.user.role == 'delivery_partner':
            raise PermissionDenied({
                "error": "NOT_DELIVERY_PARTNER",
                "message": "You must be a delivery partner to access this resource."
            })

        return True