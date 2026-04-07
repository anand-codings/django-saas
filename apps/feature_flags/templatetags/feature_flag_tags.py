"""Template tags for feature flag-gating server-rendered content.

Backed by django-waffle (already installed).  Load with:
    {% load feature_flag_tags %}
"""

from django import template

import waffle

register = template.Library()


@register.simple_tag(takes_context=True)
def feature_flag(context, flag_name):
    """Return True if the named waffle flag is active for the current request.

    Usage:
        {% feature_flag "new_dashboard" as new_dash %}
        {% if new_dash %} ... {% endif %}
    """
    request = context.get("request")
    if request is None:
        return False
    return waffle.flag_is_active(request, flag_name)


@register.simple_tag(takes_context=True)
def waffle_switch(context, switch_name):
    """Return True if the named waffle switch is active (request-independent).

    Usage:
        {% waffle_switch "maintenance_mode" as maint %}
        {% if maint %} <banner/> {% endif %}
    """
    return waffle.switch_is_active(switch_name)


@register.simple_tag(takes_context=True)
def waffle_sample(context, sample_name):
    """Return True if the current request hits the named waffle sample.

    Usage:
        {% waffle_sample "beta_feature_rollout" as in_sample %}
    """
    request = context.get("request")
    if request is None:
        return False
    return waffle.sample_is_active(sample_name)


class FeatureFlagNode(template.Node):
    """Renders child nodes only when the flag is active (block-style tag)."""

    def __init__(self, flag_name, nodelist_true, nodelist_false):
        self.flag_name = template.Variable(flag_name)
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        try:
            flag_name = self.flag_name.resolve(context)
        except template.VariableDoesNotExist:
            return self.nodelist_false.render(context)

        request = context.get("request")
        if request and waffle.flag_is_active(request, flag_name):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)


@register.tag("iffeature")
def do_feature_flag(parser, token):
    """Block-style feature flag gate.

    Usage:
        {% iffeature "new_billing_ui" %}
            <new-billing-component />
        {% else %}
            <old-billing-component />
        {% endiffeature %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(f"'{bits[0]}' tag requires exactly one argument")
    flag_name = bits[1]

    nodelist_true = parser.parse(("else", "endiffeature"))
    token = parser.next_token()
    if token.contents == "else":
        nodelist_false = parser.parse(("endiffeature",))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return FeatureFlagNode(flag_name, nodelist_true, nodelist_false)
