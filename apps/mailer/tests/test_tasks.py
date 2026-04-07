"""Tests for mailer Celery tasks."""

import uuid

import pytest

from apps.mailer.models import EmailLog
from apps.mailer.tasks import send_email_task
from conftest import EmailLogFactory


class TestSendEmailTask:
    def test_sends_email(self):
        log = EmailLogFactory(status="queued")
        send_email_task(str(log.pk))
        log.refresh_from_db()
        assert log.status == "sent"

    def test_missing_email_log(self):
        """Task should return without error for nonexistent log."""
        send_email_task(str(uuid.uuid4()))

    def test_multiple_emails(self):
        log1 = EmailLogFactory(status="queued")
        log2 = EmailLogFactory(status="queued")
        send_email_task(str(log1.pk))
        send_email_task(str(log2.pk))
        log1.refresh_from_db()
        log2.refresh_from_db()
        assert log1.status == "sent"
        assert log2.status == "sent"
