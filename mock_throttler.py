#!/usr/bin/env python3
"""
Mock throttle command listener - simulates your network engine
"""
import redis
import json
import time

def listen_for_throttle_commands():
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    pubsub = r.pubsub()
    pubsub.subscribe('throttle-commands')
    
    print("🎯 Mock Throttler listening on Redis 'throttle-commands'...")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                ip = data['ip']
                action = data['action']
                params = data.get('params', {})
                
                print(f"📨 Throttler received: {action} {ip}")
                if action == 'throttle':
                    limit = params.get('limit_mbps', 1)
                    print(f"   └─ Applying throttle: {limit} Mbps limit")
                    print(f"   └─ iptables: MARK packet for {ip}")
                    print(f"   └─ tc: Create class 1:{hash(ip) % 1000} rate {limit}mbit")
                elif action == 'unthrottle':
                    print(f"   └─ Removing throttle for {ip}")
                    print(f"   └─ iptables: Remove MARK rules for {ip}")
                    print(f"   └─ tc: Delete class for {ip}")
                
                print("✅ Command processed\n")
                
            except json.JSONDecodeError:
                print("❌ Error decoding throttle command")
            except Exception as e:
                print(f"❌ Error processing command: {e}")

if __name__ == "__main__":
    try:
        listen_for_throttle_commands()
    except KeyboardInterrupt:
        print("\n👋 Mock throttler stopped")