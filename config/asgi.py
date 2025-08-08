# config/asgi.py

import os
from django.core.asgi import get_asgi_application

# CRITICAL FIX: Run django.setup() BEFORE importing other components
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_asgi_app = get_asgi_application()

# Now that Django is set up, we can safely import our routing.
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing
import ai_tutor.routing

application = ProtocolTypeRouter({
    # Django's ASGI application to handle standard HTTP requests.
    "http": django_asgi_app,

    # WebSocket handler
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns +
            ai_tutor.routing.websocket_urlpatterns
        )
    ),
})