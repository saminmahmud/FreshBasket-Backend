from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register('users', UserViewSet, basename='user')


urlpatterns = [
    path("users/me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]