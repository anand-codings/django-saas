from rest_framework import permissions, viewsets

from apps.plans.models import Plan, PlanFeatureDefinition
from apps.plans.serializers import PlanFeatureDefinitionSerializer, PlanSerializer


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Public pricing page API — list and detail for active plans."""

    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Plan.objects.filter(status="active", is_public=True).prefetch_related("features")


class PlanFeatureDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    """List all available feature definitions (for admin/comparison)."""

    serializer_class = PlanFeatureDefinitionSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = PlanFeatureDefinition.objects.all()
