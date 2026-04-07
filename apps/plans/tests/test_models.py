"""Tests for plans models."""

import pytest
from django.db import IntegrityError

from apps.plans.models import Plan, PlanFeature, PlanFeatureDefinition
from conftest import PlanFactory, PlanFeatureDefinitionFactory, PlanFeatureFactory


class TestPlan:
    def test_create(self):
        plan = PlanFactory()
        assert plan.pk is not None
        assert plan.status == "active"

    def test_str_returns_name(self):
        plan = PlanFactory(name="Pro")
        assert str(plan) == "Pro"

    def test_slug_unique(self):
        PlanFactory(slug="pro")
        with pytest.raises(IntegrityError):
            PlanFactory(slug="pro")

    def test_default_limits(self):
        plan = PlanFactory()
        assert plan.max_members == 1
        assert plan.max_storage_mb == 100
        assert plan.max_api_calls_per_month == 1000

    def test_from_stripe_price_found(self):
        plan = PlanFactory(stripe_monthly_price_id="price_123")
        found = Plan.from_stripe_price("price_123")
        assert found == plan

    def test_from_stripe_price_not_found(self):
        assert Plan.from_stripe_price("price_nonexistent") is None

    def test_ordering(self):
        p1 = PlanFactory(sort_order=2, price_monthly=20)
        p2 = PlanFactory(sort_order=1, price_monthly=10)
        plans = list(Plan.objects.all())
        assert plans[0] == p2
        assert plans[1] == p1


class TestPlanFeature:
    def test_create_boolean(self):
        pf = PlanFeatureFactory(is_boolean=True)
        assert pf.pk is not None
        assert pf.is_boolean is True

    def test_str_boolean(self):
        plan = PlanFactory(name="Pro")
        pf = PlanFeatureFactory(plan=plan, name="SSO", is_boolean=True)
        assert str(pf) == "Pro: SSO"

    def test_str_metered(self):
        plan = PlanFactory(name="Pro")
        pf = PlanFeatureFactory(
            plan=plan, name="API Calls", is_boolean=False, limit_value=10000, limit_unit="requests"
        )
        assert str(pf) == "Pro: API Calls (10000 requests)"

    def test_unique_plan_feature_slug(self):
        plan = PlanFactory()
        PlanFeatureFactory(plan=plan, slug="sso")
        with pytest.raises(IntegrityError):
            PlanFeatureFactory(plan=plan, slug="sso")


class TestPlanFeatureDefinition:
    def test_create(self):
        pfd = PlanFeatureDefinitionFactory()
        assert pfd.pk is not None

    def test_str(self):
        pfd = PlanFeatureDefinitionFactory(name="Single Sign-On")
        assert str(pfd) == "Single Sign-On"

    def test_slug_unique(self):
        PlanFeatureDefinitionFactory(slug="sso")
        with pytest.raises(IntegrityError):
            PlanFeatureDefinitionFactory(slug="sso")
