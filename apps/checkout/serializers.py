from rest_framework import serializers


class CheckoutSessionCreateSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField(help_text="UUID of the Plan to subscribe to.")
    interval = serializers.ChoiceField(choices=["monthly", "yearly"], default="monthly")
    organization_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        default=None,
        help_text="If provided, create an org-level subscription instead of user-level.",
    )
