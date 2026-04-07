# django-saas

A modular Django monorepo with **89 standalone apps** powering a multi-tenant SaaS platform. Everything runs in Docker — no local Python, no venv, no host dependencies.

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5.1, Python 3.12 |
| APIs | Django REST Framework, Django Ninja, drf-spectacular (OpenAPI) |
| Auth | allauth + MFA, SimpleJWT, django-guardian, rules, SAML2, OIDC |
| Billing | dj-stripe (Stripe) |
| Background jobs | Celery + Redis, django-celery-beat (DB scheduler) |
| WebSockets | Channels + channels-redis |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis 7 |
| Multi-tenancy | Custom row-level (`shared`) or schema-per-tenant (`schema`) |
| AI/ML | LiteLLM, OpenAI, Anthropic, pgvector |
| Monitoring | Sentry, Prometheus, structlog, OpenTelemetry, django-health-check |
| Admin | django-unfold, django-hijack |

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY

# 2. Build and start all services
docker compose up --build

# 3. Run migrations (in a separate terminal)
docker compose exec app python manage.py migrate

# 4. Create a superuser
docker compose exec app python manage.py createsuperuser
```

The app is available at **http://localhost:16000**.

## Services

| Service | Container | Host Port | Purpose |
|---------|-----------|-----------|---------|
| `app` | Django dev server | 16000 | Web application |
| `db` | PostgreSQL 16 | 16432 | Primary database |
| `redis` | Redis 7 | 16379 | Cache + Celery broker + Channels |
| `celery_worker` | Celery worker | — | Async task processing |
| `celery_beat` | Celery beat | — | Periodic task scheduling |

In production the `app` container runs **gunicorn** with 4 workers (the Dockerfile `CMD`). Docker Compose overrides this with the Django dev server for local development.

## Project Structure

```
├── apps/                  # 89 Django apps (see Architecture below)
├── config/
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── dev.py         # DEBUG=True, console email, debug toolbar
│   │   ├── prod.py        # SSL/HSTS, secure cookies
│   │   └── test.py        # SQLite :memory:, eager Celery
│   ├── urls.py            # Root URL configuration
│   ├── celery.py          # Celery app
│   ├── asgi.py            # Channels + HTTP ASGI
│   └── wsgi.py            # WSGI entry point
├── shared/                # Cross-cutting contracts
│   ├── models/            # Base models and mixins
│   ├── providers/         # Email, storage, payment, AI, SMS abstractions
│   ├── types/             # Shared type definitions
│   ├── utils/             # Common utilities
│   ├── mixins/            # Reusable model/view mixins
│   └── validators/        # Shared validators
├── scripts/
│   └── check_boundaries.py  # Import boundary enforcement
├── docs/
│   └── DEPENDENCY_GRAPH.md  # Full app dependency map
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml         # Single dependency source (hatch)
└── .env.example
```

## Architecture

Apps are organized into **seven dependency layers**. Each layer may only import from itself or layers below it.

```
 ┌───────────────────────────────────────────────────┐
 │                  SHARED CONTRACTS                  │
 │  models · providers · types · mixins · validators  │
 └──────────────────────┬────────────────────────────┘
 ┌──────────────────────▼────────────────────────────┐
 │                  FOUNDATION                        │
 │  accounts · tenancy · organizations · app_config   │
 └──────────────────────┬────────────────────────────┘
 ┌──────────────────────▼────────────────────────────┐
 │                INFRASTRUCTURE                      │
 │  api · caching · tasks · storage · mailer          │
 │  security · health · monitoring · rate_limiting    │
 └──────────────────────┬────────────────────────────┘
 ┌──────────────────────▼────────────────────────────┐
 │                   BUSINESS                         │
 │  billing · plans · notifications · permissions     │
 │  audit_log · feature_flags · encryption · sessions │
 └──────────────────────┬────────────────────────────┘
 ┌──────────────────────▼────────────────────────────┐
 │                    FEATURE                         │
 │  profiles · invitations · sso · checkout · search  │
 │  blog · media · exports · webhooks · analytics     │
 └──────────────────────┬────────────────────────────┘
 ┌──────────────────────▼────────────────────────────┐
 │                   EXTENSION                        │
 │  comments · live_chat · feedback · experiments     │
 │  referrals · zapier_connector · developer_portal   │
 └──────────────────────┬────────────────────────────┘
 ┌──────────────────────▼────────────────────────────┐
 │                     AI/ML                          │
 │  ai_core · vector_search · ai_chat · ai_agents    │
 │  embeddings · ai_moderation · ai_usage            │
 └───────────────────────────────────────────────────┘
```

**Boundary rules:**

- No upward imports — lower layers never import from higher layers
- No cross-feature imports — feature-layer apps communicate through signals
- Shared types for cross-boundary data — never import models across layers
- Provider interfaces for external services — use `shared/providers/` abstractions

Enforce with `docker compose exec app python scripts/check_boundaries.py`. Full dependency map in `docs/DEPENDENCY_GRAPH.md`.

## Common Commands

All commands run inside Docker.

```bash
# Migrations
docker compose exec app python manage.py makemigrations
docker compose exec app python manage.py migrate

# Django shell
docker compose exec app python manage.py shell

# Tests
docker compose exec app pytest
docker compose exec app pytest apps/billing/ -v     # single app

# Linting and type checks
docker compose exec app ruff check .
docker compose exec app mypy apps/

# Boundary check
docker compose exec app python scripts/check_boundaries.py

# Collect static files
docker compose exec app python manage.py collectstatic --noinput

# Celery
docker compose logs -f celery_worker
docker compose logs -f celery_beat

# Rebuild after dependency changes
docker compose up --build
```

## Environment Variables

Copy `.env.example` to `.env` and configure. Key variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `SECRET_KEY` | Django secret key | *must set* |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | PostgreSQL connection | `postgres://postgres:postgres@db:5432/django_saas` |
| `REDIS_URL` | Redis connection | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker | `redis://redis:6379/1` |
| `TENANT_MODE` | `shared` (row-level) or `schema` (schema-per-tenant) | `shared` |
| `STRIPE_TEST_SECRET_KEY` | Stripe API key | — |
| `DJSTRIPE_WEBHOOK_SECRET` | Stripe webhook secret | — |
| `EMAIL_BACKEND` | Email backend class | `console` (dev) |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `ANTHROPIC_API_KEY` | Anthropic API key | — |
| `LITELLM_API_KEY` | LiteLLM API key | — |
| `SENTRY_DSN` | Sentry error tracking | — |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `STORAGE_BACKEND` | File storage backend | `local` |

## API Endpoints

| Path | Framework | Description |
|------|-----------|-------------|
| `/api/v1/...` | DRF | Versioned REST APIs for all domain apps |
| `/api/ninja/` | Django Ninja | Ninja-style API endpoints |
| `/api/schema/` | drf-spectacular | OpenAPI 3 schema (staff only) |
| `/api/schema/swagger-ui/` | drf-spectacular | Swagger UI (staff only) |
| `/admin/` | django-unfold | Admin dashboard |
| `/auth/` | dj-rest-auth | Authentication endpoints |
| `/accounts/` | allauth | Account management |
| `/-/health/` | django-health-check | Health checks |
| `/metrics` | django-prometheus | Prometheus metrics |

## Settings Modules

| Module | Use |
|--------|-----|
| `config.settings.dev` | Local development — `DEBUG=True`, console email, debug toolbar |
| `config.settings.prod` | Production — SSL/HSTS, secure cookies, Whitenoise |
| `config.settings.test` | Tests — SQLite in-memory, eager Celery, fast password hashers |

`manage.py` defaults to `dev`. Override with `DJANGO_SETTINGS_MODULE`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and pull request guidelines.

## Security

If you discover a security vulnerability, please report it responsibly. Do **not** open a public issue. Instead, email the maintainers directly with details of the vulnerability. We will acknowledge receipt within 48 hours and provide an expected timeline for a fix.

This project uses django-axes for brute-force protection, django-csp for Content Security Policy, django-cors-headers for CORS, and django-encrypted-model-fields for field-level encryption. See `config/settings/prod.py` for production security hardening (SSL/HSTS, secure cookies, etc.).

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
