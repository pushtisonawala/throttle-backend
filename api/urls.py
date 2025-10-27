from django.urls import path
from .views import ThrottleControlView, DeviceStatsView, GenerateProfileView, HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('throttle/', ThrottleControlView.as_view(), name='throttle-control'),
    path('devices/', DeviceStatsView.as_view(), name='device-stats'),
    path('generate-profile/', GenerateProfileView.as_view(), name='generate-profile'),
]
