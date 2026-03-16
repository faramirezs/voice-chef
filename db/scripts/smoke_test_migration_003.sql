\echo 'Running migration 003 smoke tests (wrapped in transactions, no persistent data)'

-- 1) Default yield_mode should be 'count'
BEGIN;
INSERT INTO recipes (id, name, status)
VALUES ('11111111-1111-1111-1111-111111111111', 'T_default_yield_mode', 'draft');
SELECT id, status, yield_mode
FROM recipes
WHERE id = '11111111-1111-1111-1111-111111111111';
ROLLBACK;

-- 2) Invalid yield_mode should fail
BEGIN;
SAVEPOINT s_invalid_yield_mode;
INSERT INTO recipes (id, name, status, yield_mode)
VALUES ('22222222-2222-2222-2222-222222222222', 'T_invalid_yield_mode', 'draft', 'pieces');
ROLLBACK TO SAVEPOINT s_invalid_yield_mode;
ROLLBACK;

-- 3) Active + weight without portion_size_grams should fail
BEGIN;
SAVEPOINT s_missing_portion_size;
INSERT INTO recipes (id, name, status, yield_mode)
VALUES ('33333333-3333-3333-3333-333333333333', 'T_weight_without_portion', 'active', 'weight');
ROLLBACK TO SAVEPOINT s_missing_portion_size;
ROLLBACK;

-- 4) Valid active + weight row should succeed
BEGIN;
INSERT INTO recipes (
    id,
    name,
    status,
    yield_mode,
    portion_size_grams,
    total_raw_weight_grams,
    total_cooked_weight_grams,
    portions_count_resolved
)
VALUES (
    '44444444-4444-4444-4444-444444444444',
    'T_weight_with_portion',
    'active',
    'weight',
    125.5,
    3000,
    2500,
    20
);
SELECT id, status, yield_mode, portion_size_grams, total_raw_weight_grams, total_cooked_weight_grams, portions_count_resolved
FROM recipes
WHERE id = '44444444-4444-4444-4444-444444444444';
ROLLBACK;

-- 5) Negative total_raw_weight_grams should fail
BEGIN;
SAVEPOINT s_negative_raw_weight;
INSERT INTO recipes (id, name, status, yield_mode, total_raw_weight_grams)
VALUES ('55555555-5555-5555-5555-555555555555', 'T_negative_raw_weight', 'draft', 'count', -1);
ROLLBACK TO SAVEPOINT s_negative_raw_weight;
ROLLBACK;

-- 6) Zero portions_count_resolved should fail
BEGIN;
SAVEPOINT s_zero_portions;
INSERT INTO recipes (id, name, status, yield_mode, portions_count_resolved)
VALUES ('66666666-6666-6666-6666-666666666666', 'T_zero_portions', 'draft', 'count', 0);
ROLLBACK TO SAVEPOINT s_zero_portions;
ROLLBACK;

-- 7) Realistic update flow draft -> active/weight should succeed
BEGIN;
INSERT INTO recipes (id, name, status)
VALUES ('77777777-7777-7777-7777-777777777777', 'T_update_flow', 'draft');
UPDATE recipes
SET
    yield_mode = 'weight',
    portion_size_grams = 80,
    total_raw_weight_grams = 1000,
    total_cooked_weight_grams = 900,
    portions_count_resolved = 11,
    status = 'active'
WHERE id = '77777777-7777-7777-7777-777777777777';
SELECT id, status, yield_mode, portion_size_grams, total_raw_weight_grams, total_cooked_weight_grams, portions_count_resolved
FROM recipes
WHERE id = '77777777-7777-7777-7777-777777777777';
ROLLBACK;

-- 8) Index exists and can be used for yield_mode filtering
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'recipes'
  AND indexname = 'idx_recipes_yield_mode';

SET enable_seqscan = off;
EXPLAIN SELECT id FROM recipes WHERE yield_mode = 'weight';
