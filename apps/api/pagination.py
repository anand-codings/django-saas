"""Custom pagination classes for the API."""

from rest_framework.pagination import CursorPagination, PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Default pagination: page numbers with configurable page size."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class CursorPagination(CursorPagination):
    """Cursor-based pagination for large datasets and real-time feeds.

    More efficient than offset pagination for large tables.
    """

    page_size = 25
    ordering = "-created_at"
    cursor_query_param = "cursor"
