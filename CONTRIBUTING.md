# Contributing to django-saas

Thanks for your interest in contributing! This guide covers how to get started.

## Development Setup

This project runs entirely in Docker — no local Python or virtualenv needed.

```bash
# 1. Clone the repo
git clone <repo-url> && cd django-saas

# 2. Configure environment
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY

# 3. Build and start all services
docker compose up --build

# 4. Run migrations
docker compose exec app python manage.py migrate

# 5. Create a superuser
docker compose exec app python manage.py createsuperuser
```

The app is available at `http://localhost:16000`.

## Making Changes

1. Create a branch from `main`.
2. Make your changes.
3. Run the checks below before submitting a PR.

## Code Quality

All commands run inside Docker:

```bash
# Linting (ruff)
docker compose exec app ruff check .

# Type checking (mypy)
docker compose exec app mypy apps/

# Tests
docker compose exec app pytest

# Architecture boundary enforcement
docker compose exec app python scripts/check_boundaries.py
```

## Architecture Rules

Apps are organized into seven dependency layers. **These rules are enforced:**

- No upward imports — lower layers never import from higher layers.
- No cross-feature imports — feature-layer apps communicate through signals.
- Shared types for cross-boundary data — never import models across layers.
- Provider interfaces for external services — use `shared/providers/` abstractions.

See the full dependency graph in `docs/DEPENDENCY_GRAPH.md`.

## Pull Request Process

1. Ensure all checks pass (ruff, mypy, pytest, boundary check).
2. Keep PRs focused — one feature or fix per PR.
3. Add tests for new functionality.
4. Update documentation if you change public APIs or add new apps.

## Adding a New App

1. Create the app under `apps/` in the appropriate layer directory.
2. Add it to `INSTALLED_APPS` in `config/settings/base.py`.
3. Register URL patterns in `config/urls.py` if the app has API endpoints.
4. Update `docs/DEPENDENCY_GRAPH.md` with the new app's dependencies.
5. Run `scripts/check_boundaries.py` to verify layer compliance.

## Coding Standards

- Python 3.12+, Django 5.1+
- Line length: 120 characters
- Linter: ruff (rules: E, F, I, N, W, UP, B, A, DJ)
- Type checker: mypy with django-stubs
- Test framework: pytest + pytest-django
