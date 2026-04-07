"""Celery application configuration."""

import logging
import os

from celery import Celery
from celery.signals import task_failure, task_retry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

from config.otel import init_otel  # noqa: E402

init_otel()

app = Celery("django_saas")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

logger = logging.getLogger("celery.tasks")


@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    logger.error("Task %s[%s] failed: %s", sender.name if sender else "?", task_id, exception)


@task_retry.connect
def handle_task_retry(sender=None, request=None, reason=None, **kwargs):
    logger.warning(
        "Task %s[%s] retrying: %s",
        sender.name if sender else "?",
        request.id if request else "?",
        reason,
    )
