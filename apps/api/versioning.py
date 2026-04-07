"""API versioning utilities."""

from rest_framework.versioning import URLPathVersioning


class APIVersioning(URLPathVersioning):
    """URL path-based versioning: /api/v1/, /api/v2/, etc."""

    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"
