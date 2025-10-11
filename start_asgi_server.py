#!/usr/bin/env python
"""
NetGuardian ASGI Server
Starts Django with proper ASGI support for WebSockets
"""
import os
import sys
import django
from daphne.server import Server
from daphne.endpoints import build_endpoint_description_strings

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netguardian.settings')
django.setup()

def main():
    from netguardian.asgi import application
    
    print("🚀 Starting NetGuardian with ASGI support...")
    print("📍 Server endpoints:")
    print("   • HTTP: http://localhost:8000/")
    print("   • WebSocket: ws://localhost:8000/ws/stats/")
    print("   • API: http://localhost:8000/api/throttle/")
    print("   • Admin: http://localhost:8000/admin/")
    print("\n⏹️  Press Ctrl+C to stop the server\n")
    
    # Create server
    server = Server(
        application=application,
        endpoints=build_endpoint_description_strings(host="127.0.0.1", port=8000),
        verbosity=2,
    )
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")

if __name__ == "__main__":
    main()