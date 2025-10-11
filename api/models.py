from django.db import models
from django.utils import timezone

class NetworkDevice(models.Model):
    """Model to store network device information"""
    ip_address = models.GenericIPAddressField(unique=True)
    mac_address = models.CharField(max_length=17, blank=True, null=True)  # Format: AA:BB:CC:DD:EE:FF
    hostname = models.CharField(max_length=255, blank=True, null=True)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_seen']
    
    def __str__(self):
        return f"{self.ip_address} ({self.hostname or 'Unknown'})"

class ThrottleAction(models.Model):
    """Model to log throttle/unthrottle actions"""
    ACTION_CHOICES = [
        ('throttle', 'Throttle'),
        ('unthrottle', 'Unthrottle'),
    ]
    
    device = models.ForeignKey(NetworkDevice, on_delete=models.CASCADE, related_name='throttle_actions')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    limit_mbps = models.FloatField(null=True, blank=True)  # Only for throttle actions
    reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action.title()} {self.device.ip_address} at {self.timestamp}"

class NetworkProfile(models.Model):
    """Model to store generated network profiles"""
    name = models.CharField(max_length=100)
    threshold_bytes_per_sec = models.IntegerField()
    debounce_seconds = models.IntegerField()
    rate_limit = models.CharField(max_length=20)  # e.g., "2mbit"
    questionnaire_data = models.JSONField()  # Store the original answers
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"

class NetworkStats(models.Model):
    """Model to store network statistics snapshots"""
    timestamp = models.DateTimeField(default=timezone.now)
    total_down_mbps = models.FloatField()
    total_up_mbps = models.FloatField()
    device_count = models.IntegerField()
    raw_data = models.JSONField()  # Store the complete stats payload
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Stats at {self.timestamp} - Down: {self.total_down_mbps}Mbps, Up: {self.total_up_mbps}Mbps"
