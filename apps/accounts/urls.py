"""URL configuration for the accounts app (DRF)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MeView, PasswordChangeView, UserViewSet

app_name = "accounts"

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("me/password/", PasswordChangeView.as_view(), name="password-change"),
    path("", include(router.urls)),
]
