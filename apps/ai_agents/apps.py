from django.apps import AppConfig


class AiAgentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai_agents"
    label = "ai_agents"
    verbose_name = "Agent/workflow framework: multi-step AI tasks, tool use, function calling, async execution"
