
from channels.generic.websocket import AsyncJsonWebsocketConsumer
class LiveRoomConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.code = self.scope['url_route']['kwargs']['code']
        self.group = f"room_{self.code}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)
    async def receive_json(self, content, **kwargs):
        await self.channel_layer.group_send(self.group, {"type":"broadcast","payload":content})
    async def broadcast(self, event):
        await self.send_json(event['payload'])
