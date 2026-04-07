from django.apps import AppConfig


class VectorSearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vector_search"
    label = "vector_search"
    verbose_name = "Vector embeddings storage and semantic search with provider abstraction (pgvector, Pinecone, Qdrant)"
