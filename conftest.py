"""Root conftest for pytest-django — factories and shared fixtures."""

from datetime import timedelta

import factory
import pytest
from django.utils import timezone
from rest_framework.test import APIClient


# ── Factories ──────────────────────────────────────────────────────


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.User"
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass1234")
    is_active = True


class AdminUserFactory(UserFactory):
    is_staff = True
    is_superuser = True
    username = factory.Sequence(lambda n: f"admin{n}")


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "organizations.Organization"

    name = factory.Sequence(lambda n: f"Org {n}")
    slug = factory.Sequence(lambda n: f"org-{n}")
    owner = factory.SubFactory(UserFactory)


class MembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "organizations.Membership"

    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)
    role = "member"
    is_active = True


class OrganizationInviteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "organizations.OrganizationInvite"

    organization = factory.SubFactory(OrganizationFactory)
    email = factory.Faker("email")
    role = "member"
    invited_by = factory.SubFactory(UserFactory)
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    status = "pending"


class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "tenancy.Tenant"

    name = factory.Sequence(lambda n: f"Tenant {n}")
    slug = factory.Sequence(lambda n: f"tenant-{n}")
    status = "active"


class TenantMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "tenancy.TenantMembership"

    tenant = factory.SubFactory(TenantFactory)
    user = factory.SubFactory(UserFactory)
    role = "member"


class PlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "plans.Plan"

    name = factory.Sequence(lambda n: f"Plan {n}")
    slug = factory.Sequence(lambda n: f"plan-{n}")
    status = "active"
    price_monthly = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    price_yearly = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    is_public = True


class PlanFeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "plans.PlanFeature"

    plan = factory.SubFactory(PlanFactory)
    name = factory.Sequence(lambda n: f"Feature {n}")
    slug = factory.Sequence(lambda n: f"feature-{n}")
    is_boolean = True


class PlanFeatureDefinitionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "plans.PlanFeatureDefinition"

    name = factory.Sequence(lambda n: f"FeatureDef {n}")
    slug = factory.Sequence(lambda n: f"featuredef-{n}")


class NotificationTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app_notifications.NotificationType"

    name = factory.Sequence(lambda n: f"Notif Type {n}")
    slug = factory.Sequence(lambda n: f"notif-type-{n}")
    title_template = "Test {event}"
    body_template = "Body for {event}"
    default_channels = ["in_app"]
    is_active = True


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app_notifications.Notification"

    recipient = factory.SubFactory(UserFactory)
    notification_type = factory.SubFactory(NotificationTypeFactory)
    title = "Test notification"
    body = "Test body"


class NotificationPreferenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app_notifications.NotificationPreference"

    user = factory.SubFactory(UserFactory)
    notification_type = factory.SubFactory(NotificationTypeFactory)
    channels = ["in_app", "email"]


class EmailTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "mailer.EmailTemplate"

    name = factory.Sequence(lambda n: f"Template {n}")
    slug = factory.Sequence(lambda n: f"template-{n}")
    subject = "Test Subject"
    body_text = "Test plain text"
    body_html = "<p>Test HTML</p>"


class EmailLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "mailer.EmailLog"

    to_email = factory.Faker("email")
    from_email = "noreply@example.com"
    subject = "Test Email"
    provider = "ses"
    status = "queued"


class BillingCustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "billing.BillingCustomer"

    user = factory.SubFactory(UserFactory)
    organization = None


# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Allow DB access in all tests by default."""
    pass


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def admin_user():
    return AdminUserFactory()


@pytest.fixture
def organization():
    return OrganizationFactory()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(user, api_client):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(admin_user, api_client):
    api_client.force_authenticate(user=admin_user)
    return api_client
