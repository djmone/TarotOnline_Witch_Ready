
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import tarotonline.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE','tarotonline.settings')
django_app = get_asgi_application()

application = ProtocolTypeRouter({
  'http': django_app,
  'websocket': AuthMiddlewareStack(URLRouter(tarotonline.routing.websocket_urlpatterns))
})
