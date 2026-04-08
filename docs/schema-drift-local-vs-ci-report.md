# Schema Drift: Local vs CI Divergence Report

## Executive summary
- CI drift gate passes against a fresh PostgreSQL service that is migrated from revision 001 to 011.
- Local drift gate fails against a dump-initialized database.
- Result: two valid but different schema baselines are being compared to the same SQLModel metadata.

## What is happening
- CI baseline:
  - GitHub Actions service postgres starts empty.
  - Alembic upgrades from 001 to 011.
  - Drift checks then compare models against migration-only schema.
- Local baseline:
  - Docker Compose mounts init scripts from db/init on first volume creation.
  - Dump content includes columns/indexes beyond migration-only baseline.
  - Drift checks compare models against dump-seeded schema.

## Evidence collected
- CI run (2026-04-08 14:40 UTC):
  - Gate 1 passed (upgrade to 011).
  - Gate 2 passed (no drift).
  - Gate 3 passed (17 tests).
  - Gate 4 passed for managed scope policy.
- Local run (2026-04-08 15:07 UTC):
  - Gate 1 passed.
  - Gate 2/3/4 failed with 60 diffs.
  - Log: logs/drift_gate_local.log.
- Dump proof (local init source includes richer schema artifacts):
  - db/init/01_dump.sql contains recipes fields such as description_short, serving_recommendation, batch_number.
  - db/init/01_dump.sql contains indexes such as ix_tenants_slug and ix_users_email.

## Why CI can pass while local fails
- CI and local are not checking the same database shape.
- CI validates migration chain integrity.
- Local validates compatibility with a historical/preloaded dump state.

## Best-practice recommendation
1. Keep migration-only drift gate as required CI check.
- This is the canonical reliability check for deployability from scratch.

2. Add a second dump-compatibility job in CI.
- Start DB from dump/init scripts, then run targeted compatibility checks.
- Make this required only if dump-based environments are officially supported.

3. Do not create a migration that "matches the dump" unless product ownership confirms dump schema is the new source of truth.
- If dump should be canonical: formalize that schema through explicit forward Alembic migrations.
- If migrations should be canonical: refresh/rebuild dump artifacts from migration-head schema and retire legacy dump deltas.

## Decision needed from senior dev
- Choose canonical source of truth:
  - Option A: Alembic migration head.
  - Option B: Dump-initialized schema.
- Approve one of these consistency plans:
  - Plan A (recommended): migration-head required CI + dump-compat secondary CI.
  - Plan B: converge migrations/models to dump schema via explicit new migrations.
  - Plan C: regenerate dump from migration-head and remove schema divergence at source.

## Current repository context relevant to this issue
- Workflow file: .github/workflows/schema-drift.yml
- Local compose and init path: docker-compose.yml and db/init/01_dump.sql
- Local drift evidence: logs/drift_gate_local.log
- Managed model scope involved in gate: users, tenants, recipes
