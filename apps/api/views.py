"""Shared API views and utilities."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    """API root — returns available API versions and endpoints."""
    return Response({
        "name": "Django SaaS API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth/",
            "accounts": "/api/v1/accounts/",
            "organizations": "/api/v1/organizations/",
            "billing": "/api/v1/billing/",
            "plans": "/api/v1/plans/",
            "notifications": "/api/v1/notifications/",
            "docs_swagger": "/api/docs/",
            "docs_schema": "/api/schema/",
            "docs_ninja": "/api/ninja/docs",
            "health": "/health/",
        },
    })
