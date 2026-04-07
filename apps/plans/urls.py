from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.plans.views import PlanFeatureDefinitionViewSet, PlanViewSet

app_name = "plans"

router = DefaultRouter()
router.register("", PlanViewSet, basename="plan")
router.register("features", PlanFeatureDefinitionViewSet, basename="feature-definition")

urlpatterns = [
    path("", include(router.urls)),
]
