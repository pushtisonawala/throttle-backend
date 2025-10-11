import redis
import json
import time
import threading

r = redis.Redis(host='localhost', port=6379, db=0)

mock_data = {
    "timestamp": time.time(),
    "global": {
        "total_down_mbps": 25.8,
        "total_up_mbps": 4.2
    },
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
    ],
    "events": [
        "[11:25:10 PM] Throttled 192.168.12.45 (Gaming-PC)",
        "[11:26:30 PM] Unthrottled 192.168.12.45 (Gaming-PC)"
    ]
}

def handle_throttle_commands():
    pubsub = r.pubsub()
    pubsub.subscribe('throttle-commands')
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                ip = data['ip']
                action = data['action']
                print(f"Received throttle command: {data}")
                for device in mock_data['devices']:
                    if device['ip'] == ip:
                        device['status'] = 'throttled' if action == 'throttle' else 'normal'
                        device['down_mbps'] = 1.0 if action == 'throttle' else 50.0
                        print(f"Updated {device['hostname']} to {device['status']}, down_mbps: {device['down_mbps']}")
                # Add to events
                event_time = time.strftime("%I:%M:%S %p")
                event = f"[{event_time}] {action.capitalize()}ed {ip} ({device['hostname']})"
                mock_data['events'].append(event)
                if len(mock_data['events']) > 10:
                    mock_data['events'] = mock_data['events'][-10:]
            except json.JSONDecodeError:
                print("Error decoding throttle command")

threading.Thread(target=handle_throttle_commands, daemon=True).start()

while True:
    mock_data["timestamp"] = time.time()
    r.publish('network-stats', json.dumps(mock_data))
    print("Published mock network-stats")
    time.sleep(5)