from django.urls import path, include
from .views import UserProfileView
from .views import WhatsAppBotView
urlpatterns = [
    path('sendinfo/', UserProfileView.as_view(), name='send_info'),  
    path('api-auth/', include('rest_framework.urls')),
    path('whatsapp/', WhatsAppBotView.as_view(), name='whatsapp-bot'),
]
