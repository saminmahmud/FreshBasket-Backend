from rest_framework import generics, permissions, viewsets
from django.contrib.auth import get_user_model
from .permissions import IsEmailVerified  
from .serializers import UserSerializer
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_delivery_partner']