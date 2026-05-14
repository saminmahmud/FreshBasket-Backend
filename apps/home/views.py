from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes


@api_view(["GET"])
@permission_classes([AllowAny])
def welcome_api(request):
    print("VIEW HIT") 
    return Response({
        "message": f"Welcome to {settings.PROJECT_TITLE}"
    })