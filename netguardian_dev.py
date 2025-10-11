#!/usr/bin/env python3
"""
NetGuardian Development Setup and Testing Script
This script helps you run all components of the NetGuardian backend
"""
import asyncio
import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

def run_command_async(command, description, cwd=None):
    """Run a command in a separate thread"""
    def run():
        print(f"🔄 {description}...")
        try:
            subprocess.run(command, shell=True, cwd=cwd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed: {e}")
        except KeyboardInterrupt:
            print(f"⏹️  {description} stopped")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

def main():
    print("🚀 NetGuardian Backend Development Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ manage.py not found. Please run this script from the Django project root.")
        return 1
    
    print("📋 Available commands:")
    print("1. Start Django server with ASGI (for WebSockets)")
    print("2. Start Redis listener (for network stats)")
    print("3. Test WebSocket connection")
    print("4. Test REST API")
    print("5. Run all services")
    print("6. Exit")
    
    while True:
        try:
            choice = input("\n🔽 Enter your choice (1-6): ").strip()
            
            if choice == "1":
                print("\n🌐 Starting Django with ASGI...")
                print("📍 Server will be available at:")
                print("   • WebSocket: ws://localhost:8000/ws/stats/")
                print("   • REST API: http://localhost:8000/api/throttle/")
                print("   • Admin: http://localhost:8000/admin/")
                print("\n⏹️  Press Ctrl+C to stop\n")
                os.system("daphne -b 0.0.0.0 -p 8000 netguardian.asgi:application")
                
            elif choice == "2":
                print("\n📡 Starting Redis listener...")
                print("💡 Make sure Redis server is running first!")
                print("⏹️  Press Ctrl+C to stop\n")
                os.system("python manage.py redis_listener")
                
            elif choice == "3":
                print("\n🧪 Testing WebSocket connection...")
                os.system("python test_websocket.py")
                
            elif choice == "4":
                print("\n🧪 Testing REST API...")
                test_command = '''curl -X POST http://localhost:8000/api/throttle/ -H "Content-Type: application/json" -d "{\\"ip\\": \\"192.168.1.100\\", \\"action\\": \\"throttle\\"}"'''
                os.system(test_command)
                print()
                
            elif choice == "5":
                print("\n🚀 Starting all services...")
                print("💡 This will start Django server and Redis listener")
                print("📝 Open multiple terminals to run these simultaneously:")
                print("\nTerminal 1 - Django Server:")
                print("daphne -b 0.0.0.0 -p 8000 netguardian.asgi:application")
                print("\nTerminal 2 - Redis Listener:")
                print("python manage.py redis_listener")
                print("\nTerminal 3 - Test WebSocket:")
                print("python test_websocket.py")
                
            elif choice == "6":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()