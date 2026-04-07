#!/usr/bin/env python3
"""Check that app import boundaries are respected.

Layers (bottom to top):
  0: shared
  1: foundation (accounts, tenancy, organizations, app_config, testing)
  2: infrastructure (api, caching, tasks, storage, mailer, security, health, monitoring, rate_limiting, db_utils, static_assets, api_docs, containerization)
  3: business (billing, plans, notifications, permissions, audit_log, feature_flags, encryption, sessions)
  4: feature (profiles, invitations, sso, api_keys, checkout, usage_metering, blog, pages, search, media, exports, support, onboarding, seo, compliance, webhooks_outbound, webhooks_inbound, analytics, metrics, email_templates, email_marketing, push_notifications, sms, oauth_provider, integrations, realtime, scheduled_jobs, tagging, i18n, l10n, data_portability, admin_dashboard, internal_tools, staff_permissions, user_preferences, impersonation, test_fixtures)
  5: extension (team_management, knowledge_base, comments, reactions, live_chat, feedback, announcements, experiments, referrals, waitlist, tracking, forms_builder, zapier_connector, developer_portal, sandbox, graphql_api, activity_stream, email_tracking)
  6: ai_ml (ai_core, vector_search, ai_chat, ai_agents, embeddings, ai_moderation, ai_usage)

Rule: An app at layer N may only import from layers 0..N (same or below).
Exception: Cross-layer FK references via string paths ("app.Model") are allowed in Django.

Usage:
    python scripts/check_boundaries.py
"""

import ast
import os
import sys
from collections import defaultdict

LAYER_MAP = {}

LAYERS = {
    0: ["shared"],
    1: ["accounts", "tenancy", "organizations", "app_config", "testing"],
    2: ["api", "api_docs", "caching", "tasks", "storage", "mailer", "security",
        "health", "monitoring", "rate_limiting", "db_utils", "static_assets", "containerization"],
    3: ["billing", "plans", "notifications", "permissions", "audit_log",
        "feature_flags", "encryption", "sessions"],
    4: ["profiles", "invitations", "sso", "api_keys", "checkout", "usage_metering",
        "blog", "pages", "search", "media", "exports", "support", "onboarding",
        "seo", "compliance", "webhooks_outbound", "webhooks_inbound", "analytics",
        "metrics", "email_templates", "email_marketing", "push_notifications", "sms",
        "oauth_provider", "integrations", "realtime", "scheduled_jobs", "tagging",
        "i18n", "l10n", "data_portability", "admin_dashboard", "internal_tools",
        "staff_permissions", "user_preferences", "impersonation", "test_fixtures"],
    5: ["team_management", "knowledge_base", "comments", "reactions", "live_chat",
        "feedback", "announcements", "experiments", "referrals", "waitlist",
        "tracking", "forms_builder", "zapier_connector", "developer_portal",
        "sandbox", "graphql_api", "activity_stream", "email_tracking"],
    6: ["ai_core", "vector_search", "ai_chat", "ai_agents", "embeddings",
        "ai_moderation", "ai_usage"],
}

for layer_num, apps in LAYERS.items():
    for app in apps:
        LAYER_MAP[app] = layer_num

# Known allowed cross-layer imports (exceptions to the rule)
ALLOWED_EXCEPTIONS = {
    # rate_limiting (layer 2) needs plans (layer 3) for plan-tier limits
    ("rate_limiting", "plans"),
    # billing (layer 3) needs plans (layer 3) - same layer, fine
    # ai_usage (layer 6) needs billing (layer 3) - higher can import lower, fine
}


def get_app_name(filepath):
    """Extract app name from a file path like apps/billing/models.py."""
    parts = filepath.split(os.sep)
    if "apps" in parts:
        idx = parts.index("apps")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    if "shared" in parts:
        return "shared"
    return None


def extract_imports(filepath):
    """Parse a Python file and extract all import targets."""
    try:
        with open(filepath) as f:
            tree = ast.parse(f.read())
    except (SyntaxError, FileNotFoundError):
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def get_imported_app(import_path):
    """Determine which app an import path belongs to."""
    parts = import_path.split(".")
    if parts[0] == "apps" and len(parts) > 1:
        return parts[1]
    if parts[0] == "shared":
        return "shared"
    return None


def check_boundaries():
    violations = []
    import_graph = defaultdict(set)

    for root, dirs, files in os.walk("apps"):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(root, filename)
            source_app = get_app_name(filepath)
            if source_app is None:
                continue

            source_layer = LAYER_MAP.get(source_app)
            if source_layer is None:
                continue

            for imp in extract_imports(filepath):
                target_app = get_imported_app(imp)
                if target_app is None or target_app == source_app:
                    continue

                import_graph[source_app].add(target_app)
                target_layer = LAYER_MAP.get(target_app)
                if target_layer is None:
                    continue

                # Violation: importing from a higher layer
                if target_layer > source_layer:
                    if (source_app, target_app) not in ALLOWED_EXCEPTIONS:
                        violations.append({
                            "file": filepath,
                            "source_app": source_app,
                            "source_layer": source_layer,
                            "target_app": target_app,
                            "target_layer": target_layer,
                            "import": imp,
                        })

    return violations, import_graph


def main():
    violations, import_graph = check_boundaries()

    print("=" * 60)
    print("DEPENDENCY BOUNDARY CHECK")
    print("=" * 60)

    # Print import graph summary
    print("\nImport Graph:")
    for app in sorted(import_graph.keys()):
        deps = sorted(import_graph[app])
        layer = LAYER_MAP.get(app, "?")
        print(f"  [{layer}] {app} → {', '.join(deps)}")

    print(f"\n{'=' * 60}")

    if violations:
        print(f"\n❌ {len(violations)} BOUNDARY VIOLATION(S) FOUND:\n")
        for v in violations:
            print(f"  {v['file']}")
            print(f"    {v['source_app']} (layer {v['source_layer']}) imports {v['target_app']} (layer {v['target_layer']})")
            print(f"    Import: {v['import']}")
            print()
        sys.exit(1)
    else:
        print("\n✅ No boundary violations found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
