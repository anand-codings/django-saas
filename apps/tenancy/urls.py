from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tenancy.views import TenantViewSet

app_name = "tenancy"

router = DefaultRouter()
router.register("tenants", TenantViewSet, basename="tenant")

urlpatterns = [
    path("", include(router.urls)),
]
