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

## Implementation status (started)
- Phase 0 safety check is implemented and repeatable via:
  - `make dump-blast-check`
  - script: `db/scripts/dump_upgrade_blast_check.sh`
- Latest run result:
  - `alembic upgrade head` on a fresh dump-initialized DB succeeded from `002 -> 011`.
  - `alembic_version` resolved to `011`.
  - Evidence log: `logs/dump_upgrade_blast_check.log`.
- Important note:
  - This confirms upgrade path viability, but does not remove schema divergence between dump-init and migration-only baselines.

## Why CI can pass while local fails
- CI and local are not checking the same database shape.
- CI validates migration chain integrity.
- Local validates compatibility with a historical/preloaded dump state.

## Managed diff bucketing (from local 60-diff run)

### Bucket A - dump-only legacy/orphan artifacts (remove from dump baseline)
- `recipes` extra columns only present in dump lineage, not in current managed model contract.
- Representative fields:
  - `description_short`, `serving_recommendation`, `side_dishes`
  - `preparation_time`, `waiting_time`, `cooking_time`, `shelf_life`
  - `batch_number`, `packaging`, `packaging_material`, `portion_weight`
  - `origin_fish`, `origin_location`, `notes_instructions`, `ingredient_list_custom`
  - `nutri_score_category`, `nutri_score_veg_fruits`, `allergene_source`
  - `net_weight`, `fill_weight`, `fill_quantity`, `drained_weight`, `total_weight`
- Dump-only index set flagged for removal in drift output:
  - `idx_recipes_batch_number`, `idx_recipes_is_component`, `idx_recipes_reduction_factor`, `ix_recipes_name`

Action:
- Do not add new migrations for these unless product explicitly reinstates them into model contract.
- Remove by regenerating dump from migration head.

### Bucket B - canonical objects expected by managed model/migration contract
- Core managed-schema objects currently missing or mismatched in dump-upgraded local baseline:
  - `recipes` columns expected: `preparation_time_minutes`, `cooking_time_minutes`, `shelf_life_text`
  - `recipes` canonical indexes expected: `idx_recipes_component`, `idx_recipes_name`, `idx_recipes_status`, `idx_recipes_tenant`
  - nullability/default/type canonical mismatches on:
    - `recipes.id`, `recipes.tenant_id`, `recipes.reduction_factor`, `recipes.is_component`
    - `tenants.id`, `tenants.settings`
    - `users.id`, `users.tenant_id`, `users.email`

Action:
- First fix is dump regeneration + revision alignment, not a blind patch migration.
- If mismatch remains after regenerated dump, create focused corrective migration (`012`) for residual canonical gaps.

### Bucket C - policy/ownership decisions required
- `ix_tenants_name`, `ix_tenants_slug`, `ix_users_email` appear in dump lineage but are not part of current managed model contract.

Action:
- Decide with senior dev whether these are required canonical performance indexes.
- If yes, reintroduce in model + forward migration.
- If no, treat as dump-only legacy and remove via regenerated dump baseline.

## Proposed 012 scope gate
- Do not create `012` until dump is regenerated from migration head and `02_align_alembic_revision.sql` is corrected.
- Create `012` only for post-regeneration residuals or explicitly approved Bucket C indexes.

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
- Dump upgrade blast-check evidence: logs/dump_upgrade_blast_check.log
- Managed model scope involved in gate: users, tenants, recipes
