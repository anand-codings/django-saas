"""Tests for accounts API views."""

import pytest
from django.urls import reverse
from rest_framework import status

from conftest import AdminUserFactory, UserFactory


class TestUserViewSet:
    def test_list_requires_admin(self, authenticated_client):
        url = reverse("accounts:user-list")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_as_admin(self, admin_client):
        UserFactory()
        url = reverse("accounts:user-list")
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_user(self, api_client):
        url = reverse("accounts:user-list")
        data = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "Str0ngP@ssword!",
            "password_confirm": "Str0ngP@ssword!",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "new@example.com"
        assert "profile" in response.data

    def test_create_user_password_mismatch(self, api_client):
        url = reverse("accounts:user-list")
        data = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "Str0ngP@ssword!",
            "password_confirm": "different",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_requires_admin(self, authenticated_client, user):
        url = reverse("accounts:user-detail", kwargs={"pk": user.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestMeView:
    def test_get_me(self, authenticated_client, user):
        url = reverse("accounts:me")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert "profile" in response.data

    def test_patch_me(self, authenticated_client):
        url = reverse("accounts:me")
        response = authenticated_client.patch(url, {"first_name": "Updated"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"

    def test_unauthenticated(self, api_client):
        url = reverse("accounts:me")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPasswordChangeView:
    def test_change_password(self, authenticated_client, user):
        url = reverse("accounts:password-change")
        data = {
            "current_password": "testpass1234",
            "new_password": "NewStr0ngP@ss!",
            "new_password_confirm": "NewStr0ngP@ss!",
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("NewStr0ngP@ss!")

    def test_wrong_current_password(self, authenticated_client):
        url = reverse("accounts:password-change")
        data = {
            "current_password": "wrongpassword",
            "new_password": "NewStr0ngP@ss!",
            "new_password_confirm": "NewStr0ngP@ss!",
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_mismatched_new_passwords(self, authenticated_client):
        url = reverse("accounts:password-change")
        data = {
            "current_password": "testpass1234",
            "new_password": "NewStr0ngP@ss!",
            "new_password_confirm": "different",
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
