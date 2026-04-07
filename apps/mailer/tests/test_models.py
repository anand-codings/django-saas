"""Tests for mailer models."""

import pytest
from django.db import IntegrityError

from apps.mailer.models import EmailLog, EmailTemplate
from conftest import EmailLogFactory, EmailTemplateFactory


class TestEmailTemplate:
    def test_create(self):
        t = EmailTemplateFactory()
        assert t.pk is not None
        assert t.is_active is True

    def test_str_includes_version(self):
        t = EmailTemplateFactory(name="Welcome", version=2)
        assert str(t) == "Welcome (v2)"

    def test_slug_unique(self):
        EmailTemplateFactory(slug="welcome")
        with pytest.raises(IntegrityError):
            EmailTemplateFactory(slug="welcome")

    def test_default_version_is_1(self):
        t = EmailTemplateFactory()
        assert t.version == 1


class TestEmailLog:
    def test_create(self):
        log = EmailLogFactory()
        assert log.pk is not None

    def test_default_status_is_queued(self):
        log = EmailLogFactory()
        assert log.status == "queued"

    def test_str(self):
        log = EmailLogFactory(to_email="user@example.com", subject="Hello")
        assert "user@example.com" in str(log)
        assert "Hello" in str(log)
