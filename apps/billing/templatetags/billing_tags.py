"""Billing-specific template tags.

Load with: {% load billing_tags %}
"""

from django import template

register = template.Library()


@register.filter
def format_price(amount_cents, currency="usd"):
    """Convert Stripe amount-in-cents to a human-readable price string.

    Usage: {{ plan.amount|format_price:"usd" }}  →  $29.00
    """
    try:
        cents = int(amount_cents)
    except (TypeError, ValueError):
        return amount_cents

    zero_decimal = {"jpy", "krw", "vnd", "clp", "gnf", "mga", "pyg", "rwf", "ugx", "xaf", "xof"}
    symbols = {"usd": "$", "eur": "€", "gbp": "£", "jpy": "¥", "cad": "CA$", "aud": "A$"}
    sym = symbols.get(currency.lower(), currency.upper())

    if currency.lower() in zero_decimal:
        return f"{sym}{cents:,}"
    dollars = cents / 100
    return f"{sym}{dollars:,.2f}"


@register.filter
def interval_label(interval, interval_count=1):
    """Convert a Stripe billing interval to a friendly label.

    Usage: {{ sub.plan.interval|interval_label }}  →  monthly
    """
    count = int(interval_count) if interval_count else 1
    labels = {
        "day": ("daily", f"every {count} days"),
        "week": ("weekly", f"every {count} weeks"),
        "month": ("monthly", f"every {count} months"),
        "year": ("yearly", f"every {count} years"),
    }
    short, multi = labels.get(str(interval), (str(interval), str(interval)))
    return short if count == 1 else multi


@register.simple_tag(takes_context=True)
def current_plan(context):
    """Return the active dj-stripe Subscription for the request user, or None.

    Usage: {% current_plan as sub %} {% if sub %}...{% endif %}
    """
    request = context.get("request")
    if not request or not request.user.is_authenticated:
        return None
    try:
        from djstripe.models import Subscription
        customer = getattr(request.user, "djstripe_customers", None)
        if customer is None:
            return None
        return (
            Subscription.objects.filter(
                customer__subscriber=request.user,
                status__in=["active", "trialing"],
            )
            .select_related("plan", "plan__product")
            .first()
        )
    except Exception:
        return None


@register.simple_tag(takes_context=True)
def has_feature(context, feature_name):
    """Return True if the current user's plan includes ``feature_name``.

    Looks for a ``features`` JSON field on the plan's product metadata.

    Usage: {% has_feature "team_members" as can_invite %}
    """
    sub = current_plan(context)
    if not sub:
        return False
    try:
        metadata = sub.plan.product.metadata or {}
        features = metadata.get("features", "")
        return feature_name in [f.strip() for f in features.split(",")]
    except Exception:
        return False


@register.inclusion_tag("billing/partials/plan_badge.html", takes_context=True)
def plan_badge(context):
    """Render a small colored badge showing the current plan name.

    Usage: {% plan_badge %}
    """
    sub = current_plan(context)
    plan_name = "Free"
    color = "gray"
    if sub:
        plan_name = sub.plan.product.name if sub.plan.product else sub.plan.nickname or "Paid"
        color = "brand"
    return {"plan_name": plan_name, "color": color}
