import json
from channels.generic.websocket import AsyncWebsocketConsumer

class StatsConsumer(AsyncWebsocketConsumer):
    """
    This consumer handles WebSocket connections from the React frontend.
    It adds clients to a group and forwards stats updates to them.
    """
    async def connect(self):
        # Define a group name for all stats consumers
        self.group_name = 'stats_consumers'

        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group on disconnect
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def stats_update(self, event):
        # Send the received data to the client
        stats_data = event['data']
        await self.send(text_data=json.dumps(stats_data))