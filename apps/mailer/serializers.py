from rest_framework import serializers

from apps.mailer.models import EmailLog, EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ["id", "name", "slug", "subject", "body_text", "body_html", "category", "version", "is_active"]


class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = [
            "id", "user", "template", "from_email", "to_email", "subject",
            "message_id", "provider", "status", "error", "metadata",
            "opened_at", "clicked_at", "created_at",
        ]
        read_only_fields = fields


class SendEmailSerializer(serializers.Serializer):
    to = serializers.ListField(child=serializers.EmailField(), min_length=1)
    template_slug = serializers.SlugField(required=False)
    subject = serializers.CharField(required=False, max_length=255)
    body_text = serializers.CharField(required=False, default="")
    body_html = serializers.CharField(required=False, default="")
    template_vars = serializers.DictField(required=False, default=dict)
