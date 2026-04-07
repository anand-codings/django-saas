"""Tests for accounts models."""

import pytest
from django.db import IntegrityError

from apps.accounts.models import User, UserProfile
from conftest import UserFactory


class TestUserModel:
    def test_create_user(self):
        user = UserFactory()
        assert user.pk is not None
        assert user.is_active is True
        assert user.is_email_verified is False

    def test_str_returns_email(self):
        user = UserFactory(email="test@example.com")
        assert str(user) == "test@example.com"

    def test_username_field_is_email(self):
        assert User.USERNAME_FIELD == "email"

    def test_email_unique_constraint(self):
        UserFactory(email="dup@example.com")
        with pytest.raises(IntegrityError):
            UserFactory(email="dup@example.com")

    def test_last_login_ip_null_by_default(self):
        user = UserFactory()
        assert user.last_login_ip is None

    def test_phone_number_defaults_empty(self):
        user = UserFactory()
        assert user.phone_number == ""


class TestUserProfile:
    def test_auto_created_on_user_creation(self):
        user = UserFactory()
        assert hasattr(user, "profile")
        assert isinstance(user.profile, UserProfile)

    def test_str_returns_profile_for_email(self):
        user = UserFactory(email="prof@example.com")
        assert str(user.profile) == "Profile for prof@example.com"

    def test_onboarding_defaults_false(self):
        user = UserFactory()
        assert user.profile.onboarding_completed is False

    def test_timezone_defaults_utc(self):
        user = UserFactory()
        assert user.profile.timezone == "UTC"

    def test_locale_defaults_en(self):
        user = UserFactory()
        assert user.profile.locale == "en"
