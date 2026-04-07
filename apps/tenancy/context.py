"""Thread-local / context-var storage for the current tenant.

Use this to access the active tenant outside of the request/response cycle —
for example inside Celery tasks, management commands, or signal handlers.

Usage as a context manager::

    from apps.tenancy.context import tenant_context, get_current_tenant

    with tenant_context(some_tenant):
        # anything called inside here sees `some_tenant`
        do_work()

    # or set it imperatively (e.g. at the top of a Celery task)
    from apps.tenancy.context import set_current_tenant, clear_current_tenant
    set_current_tenant(tenant)
    try:
        do_work()
    finally:
        clear_current_tenant()
"""

from __future__ import annotations

import contextvars
from contextlib import contextmanager
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from apps.tenancy.models import Tenant

_current_tenant: contextvars.ContextVar[Optional["Tenant"]] = contextvars.ContextVar(
    "current_tenant", default=None
)


def get_current_tenant() -> Optional["Tenant"]:
    """Return the tenant bound to the current execution context, or ``None``."""
    return _current_tenant.get()


def set_current_tenant(tenant: Optional["Tenant"]) -> contextvars.Token:
    """Bind *tenant* to the current execution context.

    Returns a :class:`contextvars.Token` that can be used to restore the
    previous value via ``_current_tenant.reset(token)``.
    """
    return _current_tenant.set(tenant)


def clear_current_tenant() -> None:
    """Remove the tenant from the current execution context."""
    _current_tenant.set(None)


@contextmanager
def tenant_context(tenant: Optional["Tenant"]):
    """Context manager that sets the current tenant for the duration of the block.

    The previous tenant (if any) is restored when the block exits, even on
    exception.
    """
    token = set_current_tenant(tenant)
    try:
        yield tenant
    finally:
        _current_tenant.reset(token)
