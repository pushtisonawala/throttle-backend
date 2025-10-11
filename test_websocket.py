#!/usr/bin/env python3
"""
Simple WebSocket test client for NetGuardian backend
Tests the ws://localhost:8000/ws/stats/ endpoint
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/stats/"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            print("Waiting for messages... (Press Ctrl+C to exit)")
            
            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    print(f"📊 Received stats: {json.dumps(data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"📝 Received raw message: {message}")
                    
    except websockets.exceptions.ConnectionClosed:
        print("❌ Connection closed.")
    except websockets.exceptions.InvalidStatus as e:
        print(f"❌ WebSocket connection rejected: {e}")
        print("💡 Make sure Django server is running with ASGI (not WSGI)!")
    except KeyboardInterrupt:
        print("\n👋 Disconnecting...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())