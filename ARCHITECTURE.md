# Architecture

django-saas is a modular Django monorepo with 89 apps organized into seven dependency layers.

## Layer Hierarchy

Each layer may only import from itself or layers below it. No upward or cross-feature imports.

```
Layer 0: SHARED CONTRACTS  (shared/)
Layer 1: FOUNDATION        (accounts, tenancy, organizations, app_config, testing)
Layer 2: INFRASTRUCTURE    (api, caching, tasks, storage, mailer, security, health, monitoring, rate_limiting, db_utils)
Layer 3: BUSINESS          (billing, plans, notifications, permissions, audit_log, feature_flags, encryption, sessions)
Layer 4: FEATURE           (profiles, invitations, sso, api_keys, checkout, blog, pages, search, media, exports, support, onboarding, seo, compliance, webhooks_*, analytics, email_*, push_notifications, sms, oauth_provider, integrations, realtime, scheduled_jobs, usage_metering)
Layer 5: EXTENSION         (team_management, knowledge_base, comments, reactions, live_chat, feedback, announcements, experiments, referrals, waitlist, tracking, forms_builder, zapier_connector, developer_portal, sandbox, graphql_api, activity_stream, email_tracking)
Layer 6: AI/ML             (ai_core, vector_search, ai_chat, ai_agents, embeddings, ai_moderation, ai_usage)
```

## Boundary Rules

1. **No upward imports** — a Layer 2 app never imports from Layer 3+.
2. **No cross-feature imports** — apps within the Feature and Extension layers communicate through Django signals, not direct imports.
3. **Shared types for cross-boundary data** — never import models across layers; use `shared/types/` definitions instead.
4. **Provider interfaces for external services** — use `shared/providers/` abstractions (email, storage, payment, AI, SMS).

Enforce with: `docker compose exec app python scripts/check_boundaries.py`

Full per-app dependency map: `docs/DEPENDENCY_GRAPH.md`

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `apps/` | All 89 Django apps, each self-contained with models, views, serializers, URLs, tests |
| `shared/` | Cross-cutting contracts: base models, provider interfaces, types, mixins, validators |
| `config/` | Django settings (base/dev/prod/test), root URLs, ASGI/WSGI, Celery |
| `scripts/` | Tooling (boundary checker) |
| `tests/` | Integration and E2E tests |
| `docs/` | Dependency graph and other documentation |

## API Surface

Two API frameworks coexist:

- **Django REST Framework** — versioned at `/api/v1/...` for all domain apps
- **Django Ninja** — at `/api/ninja/` with session auth by default

OpenAPI schema available at `/api/schema/` (staff only).

## Multi-Tenancy

Configurable via `TENANT_MODE` environment variable:

- `shared` — row-level isolation (all tenants share tables, filtered by tenant FK)
- `schema` — schema-per-tenant (PostgreSQL schemas via django-tenants)

## Background Processing

- **Celery workers** for async tasks (Redis broker)
- **Celery beat** for periodic scheduling (DB-backed via django-celery-beat)
- Task definitions live within each app's `tasks.py`
