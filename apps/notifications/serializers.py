from rest_framework import serializers

from apps.notifications.models import Notification, NotificationPreference, NotificationType


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = ["id", "slug", "name", "description", "category", "default_channels"]


class NotificationSerializer(serializers.ModelSerializer):
    type_slug = serializers.CharField(source="notification_type.slug", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id", "notification_type", "type_slug", "title", "body",
            "action_url", "data", "priority",
            "is_read", "read_at", "channels_sent", "created_at",
        ]
        read_only_fields = fields


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    type_slug = serializers.CharField(source="notification_type.slug", read_only=True)

    class Meta:
        model = NotificationPreference
        fields = ["id", "notification_type", "type_slug", "channels", "is_muted"]
        read_only_fields = ["id"]


class MarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    all = serializers.BooleanField(default=False)
