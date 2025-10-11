#!/usr/bin/env python
"""
Run Django with ASGI support for WebSockets
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netguardian.settings')
    
    # Configure Django to use ASGI
    import daphne.management.commands.runserver
    
    # Use daphne's runserver command which supports ASGI
    execute_from_command_line(['manage.py', 'runserver', '--asgi'])