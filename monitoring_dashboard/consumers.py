# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CNCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'cnc_status'
        
        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass  # Not needed for publishing updates from server to client

    # Receive message from CNC status updates (via asyncio or other means)
    async def update_status(self, event):
        status_data = event['status_data']

        # Send CNC status to WebSocket
        await self.send(text_data=json.dumps(status_data))
