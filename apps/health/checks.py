"""Custom health checks beyond what django-health-check provides out of the box."""

import shutil

from django.db import connection
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


class DiskUsageHealthCheck(BaseHealthCheckBackend):
    """Check that disk usage is below a configurable threshold."""

    critical_service = False

    def check_status(self):
        usage = shutil.disk_usage("/")
        percent_used = (usage.used / usage.total) * 100
        if percent_used > 90:
            raise HealthCheckException(f"Disk usage at {percent_used:.1f}%")

    def identifier(self):
        return "Disk Usage"


class DatabaseHealthCheck(BaseHealthCheckBackend):
    """Check that the default database is reachable."""

    critical_service = True

    def check_status(self):
        try:
            connection.ensure_connection()
        except Exception as e:
            raise HealthCheckException(str(e))

    def identifier(self):
        return "Database"


class CacheHealthCheck(BaseHealthCheckBackend):
    """Check that the default cache backend is reachable."""

    critical_service = True

    def check_status(self):
        from django.core.cache import cache

        try:
            cache.set("health_check_test", "ok", timeout=5)
            value = cache.get("health_check_test")
            if value != "ok":
                raise HealthCheckException("Cache GET returned unexpected value")
        except Exception as e:
            raise HealthCheckException(str(e))

    def identifier(self):
        return "Cache"
