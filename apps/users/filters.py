import django_filters
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFilter(django_filters.FilterSet):
    is_admin = django_filters.BooleanFilter(field_name='is_staff')
    is_delivery_partner = django_filters.BooleanFilter(field_name='is_delivery_partner')

    class Meta:
        model = User
        fields = ['is_delivery_partner', 'is_admin']