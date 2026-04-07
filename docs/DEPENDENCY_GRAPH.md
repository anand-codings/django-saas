# App Dependency Graph

This document maps which apps depend on which, and enforces architectural boundaries.

## Legend
- **→** = depends on (imports from)
- **Tier**: Core / Important / Nice-to-have / AI-ML
- Apps should only depend on apps in the same or lower tier
- All apps may depend on `shared/`

---

## Dependency Layers (bottom to top)

```
┌─────────────────────────────────────────────────────────┐
│                    SHARED CONTRACTS                       │
│  shared/models  shared/providers  shared/types           │
│  shared/mixins  shared/utils      shared/validators      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  FOUNDATION LAYER                         │
│  accounts  tenancy  organizations  config  testing        │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                      │
│  api  caching  tasks  storage  mailer  security          │
│  health  monitoring  rate_limiting  db_utils              │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   BUSINESS LAYER                          │
│  billing  plans  notifications  permissions  audit_log    │
│  feature_flags  encryption  sessions                      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   FEATURE LAYER                           │
│  profiles  invitations  sso  api_keys  checkout          │
│  blog  pages  search  media  exports  support            │
│  onboarding  seo  compliance  webhooks_*  analytics      │
│  email_*  push_notifications  sms  oauth_provider        │
│  integrations  realtime  scheduled_jobs  usage_metering   │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  EXTENSION LAYER                          │
│  team_management  knowledge_base  comments  reactions     │
│  live_chat  feedback  announcements  experiments          │
│  referrals  waitlist  tracking  forms_builder             │
│  zapier_connector  developer_portal  sandbox              │
│  graphql_api  activity_stream  email_tracking             │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                    AI/ML LAYER                            │
│  ai_core  vector_search  ai_chat  ai_agents              │
│  embeddings  ai_moderation  ai_usage                     │
└─────────────────────────────────────────────────────────┘
```

---

## Per-App Dependencies

### Foundation Layer
| App | Depends On |
|-----|-----------|
| `accounts` | `shared` |
| `tenancy` | `shared`, `accounts` (for TenantMembership.user FK) |
| `organizations` | `shared`, `accounts` |
| `app_config` | `shared` |
| `testing` | `shared`, `accounts` |

### Infrastructure Layer
| App | Depends On |
|-----|-----------|
| `api` | `shared` (no model deps, just API infra) |
| `api_docs` | `api` |
| `caching` | `shared`, `tenancy` (tenant-scoped keys) |
| `tasks` | `shared` (Celery infra) |
| `storage` | `shared` |
| `mailer` | `shared`, `accounts` |
| `security` | `shared`, `accounts` |
| `health` | (standalone, no app deps) |
| `monitoring` | (standalone, no app deps) |
| `rate_limiting` | `shared`, `plans` (plan-tier limits) |
| `db_utils` | (standalone, infra only) |
| `static_assets` | (standalone, infra only) |

### Business Layer
| App | Depends On |
|-----|-----------|
| `billing` | `shared`, `accounts`, `plans` |
| `plans` | `shared` |
| `notifications` | `shared`, `accounts` |
| `permissions` | `shared`, `accounts`, `organizations` |
| `audit_log` | `shared`, `accounts` |
| `feature_flags` | `shared` |
| `encryption` | `shared` |
| `sessions` | `shared`, `accounts` |

### Feature Layer
| App | Depends On |
|-----|-----------|
| `profiles` | `accounts` |
| `invitations` | `accounts`, `organizations` |
| `sso` | `accounts`, `organizations` |
| `api_keys` | `accounts`, `organizations` |
| `checkout` | `billing`, `plans` |
| `usage_metering` | `billing` |
| `blog` | `shared`, `accounts` |
| `pages` | `shared` |
| `search` | `shared`, `tenancy` |
| `webhooks_outbound` | `shared`, `tenancy` |
| `webhooks_inbound` | `shared` |
| `analytics` | `shared`, `accounts`, `tenancy` |
| `support` | `shared`, `accounts`, `organizations` |
| `compliance` | `shared`, `accounts` |

### AI/ML Layer
| App | Depends On |
|-----|-----------|
| `ai_core` | `shared`, `tenancy` |
| `vector_search` | `ai_core` |
| `ai_chat` | `ai_core`, `accounts` |
| `ai_agents` | `ai_core` |
| `embeddings` | `ai_core`, `vector_search` |
| `ai_moderation` | `ai_core` |
| `ai_usage` | `ai_core`, `billing` |

---

## Boundary Rules

1. **No upward dependencies**: A lower layer MUST NOT import from a higher layer
2. **No cross-feature imports**: Feature layer apps should not import from each other
3. **Use signals for cross-app communication**: If billing needs to notify, it fires a signal; notifications app listens
4. **Shared types for cross-boundary data**: Don't import models across layers; use shared types/enums
5. **Provider interfaces for external services**: Use `shared.providers.*` abstractions

---

## Enforcement

Run `scripts/check_boundaries.py` to verify no boundary violations exist.
