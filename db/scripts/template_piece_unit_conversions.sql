\echo '=== Template: ingredient-specific piece-unit conversions ==='
\echo 'Fill the 7 variables below with REAL grams-per-piece values before running.'

-- Replace these example values with your real business values.
\set balsamico_stck_grams 500
\set blumenkohl_stck_grams 1200
\set eier_stck_grams 58
\set gurke_stck_grams 350
\set rote_zwiebel_stk_grams 80
\set vanillezucker_stck_grams 8
\set weisswein_stck_grams 750

BEGIN;

-- NOTE:
-- psql variables are not interpolated inside DO $$...$$ blocks in this form,
-- so keep validation external and ensure all *_grams values above are > 0.

INSERT INTO public.ingredient_units (ingredient_id, unit_code, grams_per_unit, label)
VALUES
    ('f603175a-a720-5841-bd3b-8bb4b58f84f6', 'stck', :balsamico_stck_grams::numeric, 'Balsamicoessig 1 Stck in g'),
    ('1c0510ee-6447-5f10-b7ca-e52644b9de08', 'stck', :blumenkohl_stck_grams::numeric, 'Blumenkohl 1 Stck in g'),
    ('f662257f-5e60-5eb9-896a-bef62d61d485', 'stck', :eier_stck_grams::numeric, 'Eier 1 Stck in g'),
    ('a8af4063-5b26-5389-9dad-f266ae5e4333', 'stck', :gurke_stck_grams::numeric, 'Gurke 1 Stck in g'),
    ('34754ab5-53f2-594c-a99e-a952f92bead0', 'stk', :rote_zwiebel_stk_grams::numeric, 'rote zwiebel 1 Stk in g'),
    ('d690bf27-7a51-5ac2-b801-198058bd835d', 'stck', :vanillezucker_stck_grams::numeric, 'Vanillezucker 1 Stck in g'),
    ('3fd1ffda-3064-5c51-8a40-9bffda6fd925', 'stck', :weisswein_stck_grams::numeric, 'Weisswein trocken 1 Stck in g')
ON CONFLICT (ingredient_id, unit_code)
DO UPDATE SET
    grams_per_unit = EXCLUDED.grams_per_unit,
    label = EXCLUDED.label;

-- Preview inserted/updated conversions.
SELECT iu.ingredient_id, i.name AS ingredient, iu.unit_code, iu.grams_per_unit, iu.label
FROM public.ingredient_units iu
JOIN public.ingredients i ON i.id = iu.ingredient_id
WHERE iu.ingredient_id IN (
    'f603175a-a720-5841-bd3b-8bb4b58f84f6',
    '1c0510ee-6447-5f10-b7ca-e52644b9de08',
    'f662257f-5e60-5eb9-896a-bef62d61d485',
    'a8af4063-5b26-5389-9dad-f266ae5e4333',
    '34754ab5-53f2-594c-a99e-a952f92bead0',
    'd690bf27-7a51-5ac2-b801-198058bd835d',
    '3fd1ffda-3064-5c51-8a40-9bffda6fd925'
)
ORDER BY ingredient, unit_code;

COMMIT;
