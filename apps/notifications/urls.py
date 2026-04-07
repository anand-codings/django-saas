from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.notifications.views import NotificationPreferenceViewSet, NotificationViewSet

app_name = "app_notifications"

router = DefaultRouter()
router.register("", NotificationViewSet, basename="notification")
router.register("preferences", NotificationPreferenceViewSet, basename="preference")

urlpatterns = [
    path("", include(router.urls)),
]
