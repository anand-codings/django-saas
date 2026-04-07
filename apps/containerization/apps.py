from django.apps import AppConfig


class ContainerizationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.containerization"
    label = "containerization"
    verbose_name = "Docker/Compose/Kubernetes configuration and deployment utilities"
