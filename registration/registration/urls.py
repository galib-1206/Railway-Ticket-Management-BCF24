"""registration_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import HealthCheckView
urlpatterns = [
    path('v1/registration/admin/', admin.site.urls),
    path('v1/registration/api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/registration/', include('registration_management.urls')),
    path('v1/registration/healthcheck',HealthCheckView.as_view(),name='health check')
]