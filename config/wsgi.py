"""WSGI config for Django SaaS project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

from config.otel import init_otel  # noqa: E402

init_otel()

application = get_wsgi_application()
