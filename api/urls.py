from django.urls import path
from .views import ThrottleControlView, DeviceStatsView, GenerateProfileView

urlpatterns = [
    path('throttle/', ThrottleControlView.as_view(), name='throttle-control'),
    path('devices/', DeviceStatsView.as_view(), name='device-stats'),
    path('generate-profile/', GenerateProfileView.as_view(), name='generate-profile'),
]