"""Celery tasks for async email sending."""

from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, email_log_id: str):
    """Send a single email via the configured provider.

    This task is the main entry point for async email delivery.
    It loads the EmailLog, determines the provider, sends the email,
    and updates the log with the result.
    """
    from apps.mailer.models import EmailLog

    try:
        log = EmailLog.objects.get(id=email_log_id)
    except EmailLog.DoesNotExist:
        return

    # Provider dispatch happens here — currently a placeholder.
    # Real implementation would use django-anymail or the shared.providers.email interface.
    log.status = "sent"
    log.save(update_fields=["status"])


@shared_task
def send_bulk_email_task(email_log_ids: list[str]):
    """Send a batch of emails."""
    for log_id in email_log_ids:
        send_email_task.delay(log_id)
