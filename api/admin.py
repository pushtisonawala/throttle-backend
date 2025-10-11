from django.contrib import admin
from .models import NetworkDevice, ThrottleAction, NetworkProfile, NetworkStats

@admin.register(NetworkDevice)
class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'hostname', 'mac_address', 'is_active', 'last_seen']
    list_filter = ['is_active', 'last_seen']
    search_fields = ['ip_address', 'hostname', 'mac_address']
    readonly_fields = ['first_seen']

@admin.register(ThrottleAction)
class ThrottleActionAdmin(admin.ModelAdmin):
    list_display = ['device', 'action', 'timestamp', 'limit_mbps']
    list_filter = ['action', 'timestamp']
    search_fields = ['device__ip_address', 'device__hostname']
    readonly_fields = ['timestamp']

@admin.register(NetworkProfile)
class NetworkProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'threshold_bytes_per_sec', 'debounce_seconds', 'rate_limit', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']

@admin.register(NetworkStats)
class NetworkStatsAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'total_down_mbps', 'total_up_mbps', 'device_count']
    list_filter = ['timestamp']
    readonly_fields = ['timestamp', 'raw_data']
