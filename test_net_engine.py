import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, db=0)

mock_data = {
    "timestamp": time.time(),
    "devices": [
        {
            "ip": "192.168.12.45",
            "mac": "C0:35:32:1B:90:01",
            "hostname": "Rahul-iPhone",
            "down_mbps": 18.1,
            "up_mbps": 0.5,
            "status": "normal"
        },
        {
            "ip": "192.168.12.46",
            "mac": "D0:45:33:2C:91:02",
            "hostname": "Pi-Torrent",
            "down_mbps": 50.0,
            "up_mbps": 10.0,
            "status": "normal"
        }
    ]
}

while True:
    mock_data["timestamp"] = time.time()
    r.publish('network-stats', json.dumps(mock_data))
    print("Published mock data")
    time.sleep(5)