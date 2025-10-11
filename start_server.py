#!/usr/bin/env python3
"""
NetGuardian Django Server Startup Script
This script starts the Django server with ASGI support for WebSockets
"""
import subprocess
import sys
import os

def main():
    print("🚀 Starting NetGuardian Django Server with ASGI support...")
    print("📁 Working directory:", os.getcwd())
    
    # Check if manage.py exists
    if not os.path.exists('manage.py'):
        print("❌ manage.py not found. Please run this script from the Django project root.")
        return 1
    
    try:
        # Install required packages if not installed
        print("📦 Checking dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'channels[daphne]', 'channels-redis'], check=True)
        
        print("\n🌐 Starting Django development server with ASGI...")
        print("📍 WebSocket endpoint: ws://localhost:8000/ws/stats/")
        print("📍 REST API endpoint: http://localhost:8000/api/throttle/")
        print("📍 Admin panel: http://localhost:8000/admin/")
        print("\n⏹️  Press Ctrl+C to stop the server\n")
        
        # Start the server with daphne (ASGI server)
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', 
            '--settings', 'netguardian.settings'
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")
        return 0

if __name__ == "__main__":
    sys.exit(main())