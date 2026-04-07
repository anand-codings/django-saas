"""Tests for plans API views."""

import pytest
from django.urls import reverse
from rest_framework import status

from conftest import PlanFactory, PlanFeatureFactory


class TestPlanViewSet:
    def test_list_public_plans(self, api_client):
        PlanFactory(is_public=True, status="active")
        PlanFactory(is_public=True, status="active")
        url = reverse("plans:plan-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_excludes_inactive(self, api_client):
        PlanFactory(is_public=True, status="active")
        PlanFactory(is_public=True, status="inactive")
        url = reverse("plans:plan-list")
        response = api_client.get(url)
        assert len(response.data["results"]) == 1

    def test_list_excludes_non_public(self, api_client):
        PlanFactory(is_public=True, status="active")
        PlanFactory(is_public=False, status="active")
        url = reverse("plans:plan-list")
        response = api_client.get(url)
        assert len(response.data["results"]) == 1

    def test_retrieve_by_slug(self, api_client):
        plan = PlanFactory(slug="pro", is_public=True, status="active")
        PlanFeatureFactory(plan=plan, name="SSO")
        url = reverse("plans:plan-detail", kwargs={"slug": "pro"})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["slug"] == "pro"

    def test_unauthenticated_allowed(self, api_client):
        """Plans endpoint is public (AllowAny)."""
        PlanFactory(is_public=True, status="active")
        url = reverse("plans:plan-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
