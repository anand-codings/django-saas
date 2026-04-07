from django.apps import AppConfig


class TeamManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.team_management"
    label = "team_management"
    verbose_name = "Team hierarchy within organizations: departments, sub-teams, team leads"
