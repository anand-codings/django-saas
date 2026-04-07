from django.apps import AppConfig


class AiModerationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai_moderation"
    label = "ai_moderation"
    verbose_name = "Content moderation: toxicity detection, PII detection, prompt injection defense"
