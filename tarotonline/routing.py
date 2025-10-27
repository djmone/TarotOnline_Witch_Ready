
from django.urls import path
from tarot.consumers import LiveRoomConsumer
websocket_urlpatterns = [
    path('ws/room/<code>/', LiveRoomConsumer.as_asgi()),
]
