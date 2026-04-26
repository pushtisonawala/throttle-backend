import redis
import json
from django.conf import settings
from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Command(BaseCommand):
    help = 'Listens to a Redis channel and forwards messages to Django Channels'

    def handle(self, *args, **options):
        channel_layer = get_channel_layer()
        redis_host = getattr(settings, 'REDIS_HOST', '127.0.0.1')
        redis_port = getattr(settings, 'REDIS_PORT', 6379)
        r = redis.Redis(host=redis_host, port=redis_port, db=0)
        pubsub = r.pubsub()
        pubsub.subscribe('network-stats')

        self.stdout.write(self.style.SUCCESS(f'Starting Redis listener on {redis_host}:{redis_port} (network-stats)...'))

        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    # v2.0 format is handled as JSON, no changes needed
                    r.set('latest_network_stats', json.dumps(data))
                    async_to_sync(channel_layer.group_send)(
                        'stats_consumers',
                        {
                            'type': 'stats_update',
                            'data': data
                        }
                    )
                    self.stdout.write('.', ending='')
                except json.JSONDecodeError:
                    self.stdout.write(self.style.ERROR('Could not decode JSON message.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))