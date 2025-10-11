from django.urls import path
from .views import ThrottleControlView, DeviceStatsView

urlpatterns = [
    path('throttle/', ThrottleControlView.as_view(), name='throttle-control'),
    path('devices/', DeviceStatsView.as_view(), name='device-stats'),
]