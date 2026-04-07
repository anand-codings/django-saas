"""
Base Django settings for the SaaS monorepo.
All environment-specific settings inherit from this.
"""

import os
from pathlib import Path

import environ
import structlog

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    TENANT_MODE=(str, "shared"),  # "shared" (row-level) or "schema" (schema-per-tenant)
)

environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# --------------------------------------------------------------------------
# Application definition
# --------------------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    # API
    "rest_framework",
    "ninja",
    "drf_spectacular",
    "corsheaders",
    # Auth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "rest_framework_simplejwt",
    "guardian",
    "rules",
    "rest_framework_api_key",
    "oauth2_provider",
    # Billing
    "djstripe",
    # Notifications
    "push_notifications",
    # Background Tasks
    "django_celery_beat",
    "django_celery_results",
    # Caching
    "django_redis",
    # Storage
    "storages",
    "imagekit",
    # Security
    "csp",
    "axes",
    # Audit
    "auditlog",
    "simple_history",
    # Feature Flags
    "waffle",
    # Health
    "health_check",
    "health_check.contrib.celery",
    "health_check.contrib.redis",
    # Monitoring
    "django_prometheus",
    # Admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "hijack",
    # User Management
    "invitations",
    "user_sessions",
    # Content
    "markdownx",
    "taggit",
    # SEO
    "meta",
    # i18n
    "modeltranslation",
    "django_countries",
    # WebSockets
    "channels",
    # Activity
    "actstream",
    # Data Privacy
    "cookie_consent",
]

LOCAL_APPS = [
    # Core tier
    "apps.accounts",
    "apps.mfa",
    "apps.permissions",
    "apps.organizations",
    "apps.tenancy",
    "apps.billing",
    "apps.plans",
    "apps.mailer",
    "apps.notifications",
    "apps.api",
    "apps.api_docs",
    "apps.storage",
    "apps.tasks",
    "apps.caching",
    "apps.audit_log",
    "apps.rate_limiting",
    "apps.health",
    "apps.monitoring",
    "apps.security",
    "apps.app_config",
    "apps.static_assets",
    "apps.testing",
    # Important tier
    "apps.profiles",
    "apps.user_preferences",
    "apps.invitations",
    "apps.impersonation",
    "apps.api_keys",
    "apps.sso",
    "apps.usage_metering",
    "apps.checkout",
    "apps.email_templates",
    "apps.email_marketing",
    "apps.push_notifications",
    "apps.sms",
    "apps.blog",
    "apps.pages",
    "apps.webhooks_outbound",
    "apps.webhooks_inbound",
    "apps.admin_dashboard",
    "apps.internal_tools",
    "apps.staff_permissions",
    "apps.analytics",
    "apps.metrics",
    "apps.search",
    "apps.media",
    "apps.exports",
    "apps.scheduled_jobs",
    "apps.feature_flags",
    "apps.encryption",
    "apps.sessions",
    "apps.i18n",
    "apps.l10n",
    "apps.tagging",
    "apps.support",
    "apps.onboarding",
    "apps.seo",
    "apps.compliance",
    "apps.data_portability",
    "apps.oauth_provider",
    "apps.integrations",
    "apps.db_utils",
    "apps.test_fixtures",
    "apps.realtime",
    "apps.containerization",
    # Nice-to-have tier
    "apps.team_management",
    "apps.email_tracking",
    "apps.knowledge_base",
    "apps.graphql_api",
    "apps.activity_stream",
    "apps.comments",
    "apps.reactions",
    "apps.live_chat",
    "apps.feedback",
    "apps.announcements",
    "apps.experiments",
    "apps.zapier_connector",
    "apps.developer_portal",
    "apps.sandbox",
    "apps.forms_builder",
    "apps.referrals",
    "apps.waitlist",
    "apps.tracking",
    # AI/ML tier
    "apps.ai_core",
    "apps.vector_search",
    "apps.ai_chat",
    "apps.ai_agents",
    "apps.embeddings",
    "apps.ai_moderation",
    "apps.ai_usage",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# --------------------------------------------------------------------------
# Middleware
# --------------------------------------------------------------------------

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "waffle.middleware.WaffleMiddleware",
    "hijack.middleware.HijackUserMiddleware",
    "apps.tenancy.middleware.TenantMiddleware",
    "axes.middleware.AxesMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "guardian.backends.ObjectPermissionBackend",
    "rules.permissions.ObjectPermissionBackend",
]

# --------------------------------------------------------------------------
# URLs & Templates
# --------------------------------------------------------------------------

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://postgres:postgres@localhost:5432/django_saas"),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# Password validation
# --------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------
# Internationalization
# --------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static & Media files
# --------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------------------------------------------------------------------------
# REST Framework
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
}

# --------------------------------------------------------------------------
# DRF Spectacular (OpenAPI docs)
# --------------------------------------------------------------------------

SPECTACULAR_SETTINGS = {
    "TITLE": "Django SaaS API",
    "DESCRIPTION": "Comprehensive SaaS platform API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# --------------------------------------------------------------------------
# Allauth
# --------------------------------------------------------------------------

SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True

# --------------------------------------------------------------------------
# dj-rest-auth
# --------------------------------------------------------------------------

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": True,
    "TOKEN_MODEL": None,
}

# --------------------------------------------------------------------------
# Cache (Redis)
# --------------------------------------------------------------------------

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

# --------------------------------------------------------------------------
# Celery
# --------------------------------------------------------------------------

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# --------------------------------------------------------------------------
# Channels (WebSockets)
# --------------------------------------------------------------------------

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL", default="redis://localhost:6379/2")],
        },
    },
}

# --------------------------------------------------------------------------
# Email (django-anymail)
# --------------------------------------------------------------------------

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {},
    "SENDGRID_API_KEY": env("SENDGRID_API_KEY", default=""),
    "MAILGUN_API_KEY": env("MAILGUN_API_KEY", default=""),
    "POSTMARK_SERVER_TOKEN": env("POSTMARK_SERVER_TOKEN", default=""),
}
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")

# --------------------------------------------------------------------------
# Storage (cloud-agnostic)
# --------------------------------------------------------------------------

STORAGE_BACKEND = env("STORAGE_BACKEND", default="local")  # local, s3, gcs, azure

# --------------------------------------------------------------------------
# Stripe (dj-stripe)
# --------------------------------------------------------------------------

STRIPE_LIVE_SECRET_KEY = env("STRIPE_LIVE_SECRET_KEY", default="")
STRIPE_TEST_SECRET_KEY = env("STRIPE_TEST_SECRET_KEY", default="")
STRIPE_LIVE_MODE = env.bool("STRIPE_LIVE_MODE", default=False)
DJSTRIPE_WEBHOOK_SECRET = env("DJSTRIPE_WEBHOOK_SECRET", default="")
DJSTRIPE_FOREIGN_KEY_TO_FIELD = "id"

# --------------------------------------------------------------------------
# Security
# --------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'",),
        "style-src": ("'self'",),
    }
}

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hours
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]

# --------------------------------------------------------------------------
# Tenancy
# --------------------------------------------------------------------------

TENANT_MODE = env("TENANT_MODE", default="shared")  # "shared" or "schema"

# --------------------------------------------------------------------------
# AI/ML
# --------------------------------------------------------------------------

LITELLM_API_KEY = env("LITELLM_API_KEY", default="")
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")

# --------------------------------------------------------------------------
# Sentry
# --------------------------------------------------------------------------

SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=0.1)

# --------------------------------------------------------------------------
# Logging (structlog)
# --------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processors": [
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer() if DEBUG else structlog.processors.JSONRenderer(),
            ],
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
