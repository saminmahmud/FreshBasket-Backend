from rest_framework.response import Response
from rest_framework import generics, permissions, viewsets
from django.contrib.auth import get_user_model
from .permissions import IsEmailVerified  
from .serializers import CreateDeliveryPartnerSerializer, UpdateDeliveryPartnerActiveStatusSerializer, UserSerializer, UserWithProfileSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import UserFilter
from allauth.account.models import EmailAddress

User = get_user_model()


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        return Response(None)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserWithProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter


class CreateDeliveryPartnerView(generics.CreateAPIView):
    serializer_class = CreateDeliveryPartnerSerializer
    permission_classes = [permissions.IsAdminUser]
    

class UpdateDeliveryPartnerActiveStatusView(generics.UpdateAPIView):
    serializer_class = UpdateDeliveryPartnerActiveStatusSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = EmailAddress.objects.filter(user__role='delivery_partner')
    lookup_field = 'pk'