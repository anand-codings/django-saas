from django.apps import AppConfig


class GraphqlApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.graphql_api"
    label = "graphql_api"
    verbose_name = "Optional GraphQL endpoint using Strawberry Django"
