from django.urls import path
from .views import *

urlpatterns = [
    path("", UserListView.as_view(), name="users"),
    path("me/", MeView.as_view(), name="me"),
]