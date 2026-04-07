# django-saas

Modular Django monorepo with 89 standalone apps powering a multi-tenant SaaS platform. Everything runs in Docker.

## Tech Stack

- **Framework:** Django 5.1, Python 3.12
- **APIs:** Django REST Framework + Django Ninja + drf-spectacular (OpenAPI)
- **Auth:** allauth + MFA, SimpleJWT, django-guardian, rules, SAML2, OIDC
- **Billing:** dj-stripe (Stripe)
- **Background jobs:** Celery + Redis, django-celery-beat
- **WebSockets:** Channels + channels-redis
- **Database:** PostgreSQL 16
- **Cache/Broker:** Redis 7
- **Multi-tenancy:** Row-level (`shared`) or schema-per-tenant (`schema`)
- **AI/ML:** LiteLLM, OpenAI, Anthropic, pgvector
- **Monitoring:** Sentry, Prometheus, structlog, OpenTelemetry
- **Admin:** django-unfold, django-hijack

## Key Commands

All commands run inside Docker:

```bash
# Start everything
docker compose up --build

# Migrations
docker compose exec app python manage.py makemigrations
docker compose exec app python manage.py migrate

# Tests
docker compose exec app pytest
docker compose exec app pytest apps/billing/ -v     # single app

# Linting / type checks
docker compose exec app ruff check .
docker compose exec app mypy apps/

# Boundary enforcement
docker compose exec app python scripts/check_boundaries.py
```

## Architecture

Apps live in `apps/` and are organized into seven dependency layers. Each layer may only import from itself or layers below.

**Layer order (top = lowest):**
1. **Shared Contracts** (`shared/`) — base models, providers, types, mixins, validators
2. **Foundation** — accounts, tenancy, organizations, app_config
3. **Infrastructure** — api, caching, tasks, storage, mailer, security, health, monitoring, rate_limiting
4. **Business** — billing, plans, notifications, permissions, audit_log, feature_flags, encryption, sessions
5. **Feature** — profiles, invitations, sso, checkout, search, blog, media, exports, webhooks, analytics
6. **Extension** — comments, live_chat, feedback, experiments, referrals, zapier_connector, developer_portal
7. **AI/ML** — ai_core, vector_search, ai_chat, ai_agents, embeddings, ai_moderation, ai_usage

### Boundary Rules

- **No upward imports** — lower layers never import from higher layers
- **No cross-feature imports** — feature-layer apps communicate through signals
- **Shared types for cross-boundary data** — never import models across layers
- **Provider interfaces for external services** — use `shared/providers/` abstractions

## Project Layout

```
apps/           → 89 Django apps (organized by layer)
config/
  settings/
    base.py     → Shared settings
    dev.py      → DEBUG=True, console email, debug toolbar
    prod.py     → SSL/HSTS, secure cookies
    test.py     → SQLite :memory:, eager Celery
  urls.py       → Root URL configuration
  celery.py     → Celery app
  asgi.py       → Channels + HTTP ASGI
  wsgi.py       → WSGI entry point
shared/         → Cross-cutting contracts (models, providers, types, mixins, validators)
scripts/        → check_boundaries.py
tests/          → Integration/E2E tests
docs/           → DEPENDENCY_GRAPH.md
```

## Settings

- `config.settings.dev` — local development (default via manage.py)
- `config.settings.prod` — production
- `config.settings.test` — tests (pytest uses this via pyproject.toml)

Override with `DJANGO_SETTINGS_MODULE`.

## Testing

- Framework: pytest + pytest-django
- Config in `pyproject.toml` under `[tool.pytest.ini_options]`
- Root `conftest.py` enables DB access for all tests by default
- Test settings use SQLite in-memory and eager Celery

## Dependencies

Managed via `pyproject.toml` with hatch build system. Dev dependencies in `[project.optional-dependencies] dev`.
