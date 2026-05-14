from django.urls import path
from .views import *

urlpatterns = [
    path("", welcome_api, name="welcome"),
]