"""ASGI config for Django SaaS project — supports HTTP + WebSocket."""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

from config.otel import init_otel  # noqa: E402

init_otel()

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter([
                # WebSocket routes will be added by apps.realtime
            ])
        ),
    }
)
