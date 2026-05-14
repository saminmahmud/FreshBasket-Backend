from django.contrib import admin
from django.urls import path, include, re_path
from allauth.account.views import ConfirmEmailView
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),

    path("accounts/", include("allauth.urls")), 
    path("api/auth/", include("dj_rest_auth.urls")),
    re_path("^api/auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$", ConfirmEmailView.as_view(), name="account_confirm_email"),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # API schema and documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path("api/users/", include("apps.users.urls")),
    path("api/", include("apps.home.urls")),
]

# Only used in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)