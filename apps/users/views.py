from rest_framework.response import Response
from rest_framework import generics, permissions, viewsets
from django.contrib.auth import get_user_model
from .permissions import IsEmailVerified  
from .serializers import UserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import UserFilter

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
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
