"""Custom API exception handler for consistent error responses."""

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Wrap DRF's default exception handler with a consistent error shape.

    Response format:
    {
        "error": {
            "code": "validation_error",
            "message": "...",
            "details": { ... }
        }
    }
    """
    response = exception_handler(exc, context)
    if response is None:
        return None

    error_code = _get_error_code(exc)
    error_data = {
        "error": {
            "code": error_code,
            "message": _get_error_message(exc, response),
            "details": response.data if isinstance(response.data, dict) else {"detail": response.data},
        }
    }
    response.data = error_data
    return response


def _get_error_code(exc):
    """Map exception type to a machine-readable error code."""
    from rest_framework import exceptions

    code_map = {
        exceptions.ValidationError: "validation_error",
        exceptions.AuthenticationFailed: "authentication_failed",
        exceptions.NotAuthenticated: "not_authenticated",
        exceptions.PermissionDenied: "permission_denied",
        exceptions.NotFound: "not_found",
        exceptions.MethodNotAllowed: "method_not_allowed",
        exceptions.Throttled: "rate_limited",
    }
    return code_map.get(type(exc), "error")


def _get_error_message(exc, response):
    """Extract a human-readable error message."""
    if hasattr(exc, "detail"):
        if isinstance(exc.detail, str):
            return exc.detail
        if isinstance(exc.detail, list):
            return exc.detail[0] if exc.detail else "An error occurred."
    return "An error occurred."
