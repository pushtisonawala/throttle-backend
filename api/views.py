import redis
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

r = redis.Redis(host='localhost', port=6379, db=0)

class ThrottleControlView(APIView):
    def post(self, request, *args, **kwargs):
        ip_address = request.data.get('ip')
        action = request.data.get('action')
        if not ip_address or not action or action not in ['throttle', 'unthrottle']:
            return Response(
                {'error': "Missing or invalid 'ip' or 'action' parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )
        command = {
            'ip': ip_address,
            'action': action,
        }
        if action == 'throttle':
            command['params'] = {'limit_mbps': 1}
        try:
            r.publish('throttle-commands', json.dumps(command))
        except redis.exceptions.ConnectionError as e:
            return Response(
                {'error': f'Could not connect to Redis: {e}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response(
            {'status': 'command sent', 'command': command},
            status=status.HTTP_200_OK
        )

class DeviceStatsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Use Redis to store the latest network-stats
            latest_stats = r.get('latest_network_stats')
            if not latest_stats:
                return Response(
                    {'error': 'No network stats available'},
                    status=status.HTTP_404_NOT_FOUND
                )
            stats = json.loads(latest_stats)
            return Response(stats, status=status.HTTP_200_OK)
        except redis.exceptions.ConnectionError as e:
            return Response(
                {'error': f'Could not connect to Redis: {e}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )