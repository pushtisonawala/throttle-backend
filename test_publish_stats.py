#!/usr/bin/env python3
"""
Test script to publish mock network stats to Redis
"""
import redis
import json
import time

# Connect to Redis
r = redis.Redis(host='127.0.0.1', port=6379, db=0)

# Mock network stats data
mock_stats = {
    "timestamp": time.time(),
    "global": {
        "total_down_mbps": 15.2,
        "total_up_mbps": 3.8
    },
    "devices": [
        {
            "ip": "10.42.0.140",
            "mac": "aa:bb:cc:dd:ee:ff",
            "hostname": "test-device",
            "down_mbps": 12.1,
            "up_mbps": 2.3,
            "status": "normal"
        },
        {
            "ip": "10.42.0.141", 
            "mac": "11:22:33:44:55:66",
            "hostname": "another-device",
            "down_mbps": 3.1,
            "up_mbps": 1.5,
            "status": "normal"
        }
    ],
    "events": [
        "[10:42:15] System monitoring started",
        "[10:42:30] Detected new device 10.42.0.140"
    ]
}

print("Publishing test network stats to Redis...")
result = r.publish('network-stats', json.dumps(mock_stats))
print(f"Published to {result} subscribers")
print("Mock stats sent:")
print(json.dumps(mock_stats, indent=2))