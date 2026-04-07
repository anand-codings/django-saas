from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import include, path
from django_prometheus.exports import ExportToDjangoView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from health_check.views import HealthCheckView
from ninja import NinjaAPI
from ninja.security import django_auth

# Django Ninja API instance — all endpoints require session auth by default.
# Individual endpoints can opt out with auth=None for public access.
ninja_api = NinjaAPI(
    title="Django SaaS API (Ninja)",
    version="1.0.0",
    urls_namespace="ninja",
    auth=django_auth,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Django Ninja API
    path("api/ninja/", ninja_api.urls),

    # Stripe webhooks (dj-stripe)
    path("stripe/", include("djstripe.urls", namespace="djstripe")),

    # Auth
    path("accounts/", include("allauth.urls")),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),

    # OAuth2 Provider
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),

    # Hijack (impersonation)
    path("hijack/", include("hijack.urls")),

    # Markdownx
    path("markdownx/", include("markdownx.urls")),

    # Health checks
    path("health/", HealthCheckView.as_view(), name="health-check"),

    # Django Prometheus (staff-only)
    path("metrics/", staff_member_required(ExportToDjangoView), name="prometheus-metrics"),

    # App URLs — Core
    path("api/v1/accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("api/v1/organizations/", include("apps.organizations.urls", namespace="organizations")),
    path("api/v1/billing/", include("apps.billing.urls", namespace="billing")),
    path("api/v1/plans/", include("apps.plans.urls", namespace="plans")),
    path("api/v1/notifications/", include("apps.notifications.urls", namespace="app_notifications")),
    path("api/v1/storage/", include("apps.storage.urls", namespace="storage")),

    # App URLs — Important
    path("api/v1/profiles/", include("apps.profiles.urls", namespace="profiles")),
    path("api/v1/invitations/", include("apps.invitations.urls", namespace="app_invitations")),
    path("api/v1/api-keys/", include("apps.api_keys.urls", namespace="api_keys")),
    path("api/v1/checkout/", include("apps.checkout.urls", namespace="checkout")),
    path("api/v1/blog/", include("apps.blog.urls", namespace="blog")),
    path("api/v1/pages/", include("apps.pages.urls", namespace="pages")),
    path("api/v1/webhooks/", include("apps.webhooks_outbound.urls", namespace="webhooks_outbound")),
    path("api/v1/webhooks/inbound/", include("apps.webhooks_inbound.urls", namespace="webhooks_inbound")),
    path("api/v1/analytics/", include("apps.analytics.urls", namespace="analytics")),
    path("api/v1/search/", include("apps.search.urls", namespace="search")),
    path("api/v1/exports/", include("apps.exports.urls", namespace="exports")),
    path("api/v1/feature-flags/", include("apps.feature_flags.urls", namespace="feature_flags")),
    path("api/v1/support/", include("apps.support.urls", namespace="support")),
    path("api/v1/onboarding/", include("apps.onboarding.urls", namespace="onboarding")),
    path("api/v1/compliance/", include("apps.compliance.urls", namespace="compliance")),
    path("api/v1/integrations/", include("apps.integrations.urls", namespace="integrations")),

    # App URLs — Nice-to-have
    path("api/v1/knowledge-base/", include("apps.knowledge_base.urls", namespace="knowledge_base")),
    path("api/v1/comments/", include("apps.comments.urls", namespace="comments")),
    path("api/v1/feedback/", include("apps.feedback.urls", namespace="feedback")),
    path("api/v1/referrals/", include("apps.referrals.urls", namespace="referrals")),
    path("api/v1/waitlist/", include("apps.waitlist.urls", namespace="waitlist")),

    # App URLs — AI/ML
    path("api/v1/ai/", include("apps.ai_core.urls", namespace="ai_core")),
    path("api/v1/ai/chat/", include("apps.ai_chat.urls", namespace="ai_chat")),
    path("api/v1/ai/search/", include("apps.vector_search.urls", namespace="vector_search")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
