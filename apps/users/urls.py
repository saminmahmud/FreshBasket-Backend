from django.urls import path
from .views import *

urlpatterns = [
    path("users/", UserListView.as_view(), name="users"),
    path("users/me/", MeView.as_view(), name="me"),
]