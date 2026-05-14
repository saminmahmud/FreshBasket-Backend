from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .permissions import IsEmailVerified  
from .serializers import UserSerializer

User = get_user_model()


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser, IsEmailVerified]