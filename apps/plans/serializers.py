from rest_framework import serializers

from apps.plans.models import Plan, PlanFeature, PlanFeatureDefinition


class PlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ["id", "name", "slug", "description", "is_boolean", "limit_value", "limit_unit"]


class PlanSerializer(serializers.ModelSerializer):
    features = PlanFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = [
            "id", "name", "slug", "description", "status",
            "price_monthly", "price_yearly", "currency",
            "max_members", "max_storage_mb", "max_api_calls_per_month",
            "is_public", "is_featured", "trial_days", "sort_order",
            "features", "created_at",
        ]


class PlanFeatureDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeatureDefinition
        fields = ["id", "name", "slug", "description", "category"]
