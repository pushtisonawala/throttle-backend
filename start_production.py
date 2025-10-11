#!/usr/bin/env python3
"""
NetGuardian Production Startup Script
Starts the NetGuardian backend with proper production settings
"""
import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def check_dependencies():
    """Check if all required services are available"""
    print("🔍 Checking dependencies...")
    
    # Check Redis
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("💡 Make sure Redis server is running: sudo systemctl start redis")
        return False
    
    # Check environment variables
    from decouple import config
    if not config('GEMINI_API_KEY', default=None):
        print("⚠️  GEMINI_API_KEY not set - AI profile generation will be disabled")
    
    if config('SECRET_KEY', default=None) == 'django-insecure-change-this-in-production':
        print("⚠️  Using default SECRET_KEY - change this in production!")
    
    return True

def run_migrations():
    """Run Django migrations"""
    print("🔄 Running database migrations...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ Migrations completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        return False
    return True

def collect_static():
    """Collect static files"""
    print("📁 Collecting static files...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], check=True)
        print("✅ Static files collected")
    except subprocess.CalledProcessError as e:
        print(f"❌ Static collection failed: {e}")
        return False
    return True

def start_server():
    """Start the ASGI server"""
    print("🚀 Starting NetGuardian server...")
    print("📍 Endpoints:")
    print("   • HTTP API: http://localhost:8000/api/")
    print("   • WebSocket: ws://localhost:8000/ws/stats/")
    print("   • Admin: http://localhost:8000/admin/")
    print("\n⏹️  Press Ctrl+C to stop\n")
    
    try:
        subprocess.run(['daphne', '-b', '0.0.0.0', '-p', '8000', 'netguardian.asgi:application'])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except FileNotFoundError:
        print("❌ Daphne not found. Install with: pip install daphne")
        return False
    return True

def main():
    print("🚀 NetGuardian Production Startup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ manage.py not found. Please run this script from the Django project root.")
        return 1
    
    # Run checks
    if not check_dependencies():
        return 1
    
    # Run migrations
    if not run_migrations():
        return 1
    
    # Start server
    if not start_server():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())