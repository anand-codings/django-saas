"""Health check views for load balancer and Kubernetes probes."""

from django.http import JsonResponse


def liveness(request):
    """Kubernetes liveness probe — always returns 200 if the process is running."""
    return JsonResponse({"status": "ok"})
