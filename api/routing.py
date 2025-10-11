from django.urls import path
from .consumers import StatsConsumer

websocket_urlpatterns = [
    path('ws/stats/', StatsConsumer.as_asgi()),
]