import redis
import json
import os
import google.generativeai as genai
from django.conf import settings
from django.utils import timezone
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NetworkDevice, ThrottleAction, NetworkProfile, NetworkStats

# Initialize Redis connection
try:
    r = redis.Redis(
        host=getattr(settings, 'REDIS_HOST', '127.0.0.1'), 
        port=getattr(settings, 'REDIS_PORT', 6379), 
        db=0,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # Test connection
    r.ping()
except redis.exceptions.ConnectionError:
    r = None

# Configure Gemini LLM
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class HealthCheckView(APIView):
    """Health check endpoint for monitoring system status"""
    
    def get(self, request, *args, **kwargs):
        status_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'services': {}
        }
        
        # Check database
        try:
            connection.ensure_connection()
            status_data['services']['database'] = 'connected'
        except Exception as e:
            status_data['services']['database'] = f'error: {str(e)}'
            status_data['status'] = 'unhealthy'
        
        # Check Redis
        if r:
            try:
                r.ping()
                status_data['services']['redis'] = 'connected'
            except Exception as e:
                status_data['services']['redis'] = f'error: {str(e)}'
                status_data['status'] = 'unhealthy'
        else:
            status_data['services']['redis'] = 'not configured'
            status_data['status'] = 'degraded'
        
        # Check AI service
        if settings.GEMINI_API_KEY:
            status_data['services']['ai_generation'] = 'configured'
        else:
            status_data['services']['ai_generation'] = 'not configured'
        
        # Response status code based on health
        response_status = status.HTTP_200_OK
        if status_data['status'] == 'unhealthy':
            response_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif status_data['status'] == 'degraded':
            response_status = status.HTTP_200_OK
            
        return Response(status_data, status=response_status)

class ThrottleControlView(APIView):
    def post(self, request, *args, **kwargs):
        if not r:
            return Response(
                {'error': 'Redis connection not available'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
        ip_address = request.data.get('ip')
        action = request.data.get('action')
        limit_mbps = request.data.get('limit_mbps', 1.0)
        reason = request.data.get('reason', '')
        
        if not ip_address or not action or action not in ['throttle', 'unthrottle']:
            return Response(
                {'error': "Missing or invalid 'ip' or 'action' parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get or create device record
        device, created = NetworkDevice.objects.get_or_create(
            ip_address=ip_address,
            defaults={'last_seen': timezone.now()}
        )
        if not created:
            device.last_seen = timezone.now()
            device.save()
        
        command = {
            'ip': ip_address,
            'action': action,
        }
        if action == 'throttle':
            command['params'] = {'limit_mbps': limit_mbps}
            
        try:
            r.publish('throttle-commands', json.dumps(command))
            
            # Log the action
            ThrottleAction.objects.create(
                device=device,
                action=action,
                limit_mbps=limit_mbps if action == 'throttle' else None,
                reason=reason
            )
            
        except redis.exceptions.ConnectionError as e:
            return Response(
                {'error': f'Could not connect to Redis: {e}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
        return Response(
            {'status': 'command sent', 'command': command, 'device_id': device.id},
            status=status.HTTP_200_OK
        )

class DeviceStatsView(APIView):
    def get(self, request, *args, **kwargs):
        if not r:
            return Response(
                {'error': 'Redis connection not available'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
        try:
            latest_stats = r.get('latest_network_stats')
            if not latest_stats:
                return Response(
                    {'error': 'No network stats available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            stats = json.loads(latest_stats)
            
            # Store stats in database for historical tracking
            NetworkStats.objects.create(
                total_down_mbps=stats.get('global', {}).get('total_down_mbps', 0),
                total_up_mbps=stats.get('global', {}).get('total_up_mbps', 0),
                device_count=len(stats.get('devices', [])),
                raw_data=stats
            )
            
            # Update device records
            for device_data in stats.get('devices', []):
                ip = device_data.get('ip')
                if ip:
                    device, created = NetworkDevice.objects.get_or_create(
                        ip_address=ip,
                        defaults={
                            'mac_address': device_data.get('mac'),
                            'hostname': device_data.get('hostname'),
                            'last_seen': timezone.now()
                        }
                    )
                    if not created:
                        device.mac_address = device_data.get('mac') or device.mac_address
                        device.hostname = device_data.get('hostname') or device.hostname
                        device.last_seen = timezone.now()
                        device.is_active = True
                        device.save()
                        
            return Response(stats, status=status.HTTP_200_OK)
            
        except redis.exceptions.ConnectionError as e:
            return Response(
                {'error': f'Could not connect to Redis: {e}'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid network stats format'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GenerateProfileView(APIView):
    SYSTEM_PROMPT = """
    You are a Network Configuration Expert assistant. Your sole purpose is to translate a user's answers from a multiple-choice questionnaire into a structured JSON configuration object for the NetGuardian system.

    You will receive a JSON object with the user's answers. Analyze the combination of answers to determine the optimal values for THRESH_BYTES_PER_SEC, DEBOUNCE_SECS, and RATE.

    *Your Logic Guidelines:*
    -   *Environment is the baseline:* 'hostel' and 'cafe' settings should be much stricter (lower thresholds, faster debounce) than 'home' or 'power_user'.
    -   *Priority is the key modifier:* If the priority is 'video_calls' or 'gaming', the debounce should be very fast and the throttle aggressive to protect latency. If the priority is 'fast_downloads', the threshold can be higher.
    -   *Tolerance maps to debounce:* 'immediately' should be a very low DEBOUNCE_SECS (e.g., 3-4s). 'only_if_huge_problem' should be a high DEBOUNCE_SECS (e.g., 15-20s).

    You MUST respond with ONLY a valid JSON object containing these exact fields:
    {
        "profile_name": "string",
        "THRESH_BYTES_PER_SEC": integer,
        "DEBOUNCE_SECS": integer,
        "RATE": "string with unit (e.g., '2mbit')"
    }
    """

    def post(self, request, *args, **kwargs):
        if not settings.GEMINI_API_KEY:
            return Response(
                {'error': 'AI profile generation not configured. Missing API key.'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
        answers = request.data.get('answers')
        profile_name = request.data.get('profile_name', 'Generated Profile')
        
        if not answers or not isinstance(answers, dict):
            return Response(
                {'error': 'Invalid "answers" payload'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Construct prompt
        user_input_json = json.dumps(answers, indent=2)
        full_prompt = f"{self.SYSTEM_PROMPT}\n\nUSER'S ANSWERS (JSON INPUT):\n{user_input_json}\n\nYOUR JSON RESPONSE (JSON OUTPUT):"

        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(full_prompt)
            llm_output_text = response.text.strip()

            # Clean LLM output if needed (remove backticks or markdown)
            if llm_output_text.startswith('```json'):
                llm_output_text = llm_output_text.split('```json')[1].rsplit('```', 1)[0].strip()
            elif llm_output_text.startswith('```'):
                llm_output_text = llm_output_text.split('```')[1].rsplit('```', 1)[0].strip()

            config_data = json.loads(llm_output_text)
            
            # Validate required fields
            required_fields = ['profile_name', 'THRESH_BYTES_PER_SEC', 'DEBOUNCE_SECS', 'RATE']
            if not all(field in config_data for field in required_fields):
                raise ValueError("Missing required fields in generated config")
            
            # Save to database
            profile = NetworkProfile.objects.create(
                name=config_data.get('profile_name', profile_name),
                threshold_bytes_per_sec=config_data['THRESH_BYTES_PER_SEC'],
                debounce_seconds=config_data['DEBOUNCE_SECS'],
                rate_limit=config_data['RATE'],
                questionnaire_data=answers
            )
            
            config_data['profile_id'] = profile.id
            return Response(config_data, status=status.HTTP_200_OK)
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'LLM returned invalid JSON format'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': f'Profile generation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )