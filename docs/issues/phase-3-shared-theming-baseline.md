# Issue: Create Shared Theming Baseline For Kitchen + Office

## Summary
Defer cross-frontend visual unification into a dedicated follow-up initiative after kitchen-only migration is stable.

## Problem
Kitchen and office currently diverge in design tokens, base CSS semantics, and reusable visual primitives. This creates visual inconsistency and repeated styling logic.

## Goal
Introduce a shared theming baseline consumable by both frontends while keeping runtime behavior and backend integrations unchanged.

## Scope
- Define shared semantic tokens for color, typography, spacing, radius, and elevation.
- Provide a shared token source and import path for both apps.
- Migrate office and kitchen to consume the shared token source.
- Optionally extract shared UI utility helpers only where reuse is proven.

## Out Of Scope
- Backend API changes.
- Routing or state-management rewrites.
- Kitchen agent behavior changes.
- Office feature rewrites.

## Acceptance Criteria
- Both frontends consume the same shared token source.
- No regressions in kitchen chat behavior or office workflows.
- Responsive visual consistency improves across key controls and layout surfaces.
- Work is delivered in incremental, reviewable PR slices.

## Suggested Implementation Sequence
1. Create shared token layer and baseline style contract.
2. Adopt tokens in office with no behavior change.
3. Adopt tokens in kitchen with no behavior change.
4. Perform cross-frontend visual QA on desktop and mobile breakpoints.

## Dependencies
- Kitchen-only visual migration merged and validated.
- Repository hygiene for generated frontend artifacts in place.

## Labels
- frontend
- design-system
- tech-debt
- follow-up
