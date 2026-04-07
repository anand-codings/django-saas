"""Shared template tags and filters used across all server-rendered pages.

Load in templates with: {% load saas_tags %}
"""

import math
from decimal import Decimal, InvalidOperation

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince

register = template.Library()


# ── Filters ──────────────────────────────────────────────────────────────────


@register.filter
def format_currency(amount, currency="USD"):
    """Render a decimal amount as a currency string.

    Usage: {{ plan.price|format_currency:"USD" }}
    Output: $29.00
    """
    try:
        value = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        return amount

    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CAD": "CA$", "AUD": "A$"}
    symbol = symbols.get(currency.upper(), currency)
    decimals = 0 if currency.upper() == "JPY" else 2
    return f"{symbol}{value:,.{decimals}f}"


@register.filter
def time_ago(dt):
    """Human-friendly relative time (e.g. '3 hours ago').

    Usage: {{ comment.created_at|time_ago }}
    """
    if not dt:
        return ""
    return f"{timesince(dt)} ago"


@register.filter
def reading_time(text, wpm=200):
    """Estimate reading time in minutes from a block of text.

    Usage: {{ post.body|reading_time }} min read
    """
    if not text:
        return 0
    word_count = len(str(text).split())
    return max(1, math.ceil(word_count / wpm))


@register.filter
def initials(user):
    """Return up to 2-letter initials from a user object.

    Usage: {{ request.user|initials }}
    """
    if not user:
        return ""
    fn = getattr(user, "first_name", "")
    ln = getattr(user, "last_name", "")
    if fn and ln:
        return f"{fn[0]}{ln[0]}".upper()
    if fn:
        return fn[0].upper()
    email = getattr(user, "email", "")
    return email[0].upper() if email else "?"


@register.filter
def percentage(value, total):
    """Compute value/total as a 0-100 integer percentage.

    Usage: {{ used|percentage:limit }}%
    """
    try:
        pct = (float(value) / float(total)) * 100
        return min(100, max(0, round(pct)))
    except (TypeError, ZeroDivisionError):
        return 0


@register.filter
def yesno_icon(value):
    """Return an HTML checkmark or cross icon based on truthiness.

    Usage: {{ feature.enabled|yesno_icon }}
    """
    if value:
        return mark_safe('<span class="text-green-500" aria-label="Yes">&#10003;</span>')
    return mark_safe('<span class="text-red-400" aria-label="No">&#10007;</span>')


# ── Tags ─────────────────────────────────────────────────────────────────────


@register.simple_tag(takes_context=True)
def tenant_url(context, path=""):
    """Build a URL scoped to the current tenant's subdomain (if applicable).

    Usage: {% tenant_url '/dashboard/' %}
    """
    request = context.get("request")
    if not request:
        return path
    tenant = getattr(request, "tenant", None)
    if tenant and getattr(tenant, "subdomain", None):
        scheme = request.scheme
        host_parts = request.get_host().split(".", 1)
        base_domain = host_parts[-1] if len(host_parts) > 1 else request.get_host()
        return f"{scheme}://{tenant.subdomain}.{base_domain}{path}"
    return path


@register.inclusion_tag("shared/partials/avatar.html")
def user_avatar(user, size="md"):
    """Render a user avatar (image or initials fallback).

    Usage: {% user_avatar request.user size="sm" %}
    """
    size_classes = {
        "xs": "w-6 h-6 text-xs",
        "sm": "w-8 h-8 text-sm",
        "md": "w-10 h-10 text-sm",
        "lg": "w-14 h-14 text-base",
        "xl": "w-20 h-20 text-lg",
    }
    return {
        "user": user,
        "size_class": size_classes.get(size, size_classes["md"]),
        "initials_val": initials(user),
    }


@register.simple_tag
def active_link(request, url_name, css_class="active"):
    """Return ``css_class`` when the current URL matches ``url_name``.

    Usage: <a href="..." class="{% active_link request 'blog:list' 'font-bold' %}">Blog</a>
    """
    from django.urls import reverse, NoReverseMatch
    try:
        path = reverse(url_name)
        if request.path == path:
            return css_class
    except NoReverseMatch:
        pass
    return ""
