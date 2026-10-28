from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from academy.views import HealthView, StudentRegistrationView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthView.as_view(), name="health"),
    path("api/auth/register/", StudentRegistrationView.as_view(), name="register"),
    path("api/auth/token/", obtain_auth_token, name="api-token-auth"),
    path("api/", include("academy.urls")),
]
