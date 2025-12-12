from django.urls import path, include
from .views import UserProfileView
from .views import *
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', index, name='index'),
    path('', UserProfileView.as_view(), name='send_info'),  
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('whatsapp/', WhatsAppBotView.as_view(), name='whatsapp-bot'),
    path('farmer/onboard/', CreateFarmerView.as_view(), name='farmer-onboard'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),

    # Auth Endpoints
    path('api/auth/', include('dj_rest_auth.urls')),                # Login, Logout, Password Reset
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')), # Register
]

