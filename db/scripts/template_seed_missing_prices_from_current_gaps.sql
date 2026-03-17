-- Fill missing ingredient prices from current coverage gaps
-- Generated on 2026-03-17
-- 1) Replace NULL eur_per_gram values below
-- 2) Run: docker compose exec -T db psql -U recipe_user -d recipe_db < db/scripts/template_seed_missing_prices_from_current_gaps.sql

BEGIN;

WITH latest_price AS (
    SELECT * FROM public.ingredient_prices_latest
), gaps AS (
    SELECT i.id, i.name, COUNT(*) AS missing_lines, COUNT(DISTINCT ri.recipe_id) AS affected_recipes
    FROM recipe_ingredients ri
    JOIN ingredients i ON i.id = ri.ingredient_id
    LEFT JOIN latest_price lp ON lp.ingredient_id = ri.ingredient_id
    WHERE ri.quantity_grams IS NULL OR lp.price_per_gram IS NULL
    GROUP BY i.id, i.name
), ranked AS (
    SELECT id, name, missing_lines, affected_recipes,
           ROW_NUMBER() OVER (ORDER BY missing_lines DESC, affected_recipes DESC, name) AS rn,
           COUNT(*) OVER () AS cnt
    FROM gaps
), price_inputs (ingredient_id, ingredient_name, eur_per_gram) AS (
    VALUES
    ('45b3b564-77d3-5ab5-949e-3dd033c9e60a'::uuid, 'zucker', NULL::numeric), -- missing_lines=9 affected_recipes=9
    ('89fe6919-c100-58d8-8dde-c1d45fb7f0a8'::uuid, 'petersilie (frisch)', NULL::numeric), -- missing_lines=8 affected_recipes=8
    ('0ce9bcb9-1b5f-5957-92b2-6ad231d954e4'::uuid, 'zwiebel', NULL::numeric), -- missing_lines=8 affected_recipes=8
    ('453a4973-48e4-5d94-80e6-10f7dac451ab'::uuid, 'rotwein (trocken)', NULL::numeric), -- missing_lines=5 affected_recipes=5
    ('ceee12dd-e269-5684-a194-96929bebc9b5'::uuid, 'Sonnenblumenprotein trocken', NULL::numeric), -- missing_lines=5 affected_recipes=4
    ('b5f9bde0-7373-5cbb-b805-899f00923cbe'::uuid, 'Geräuchertes Paprika', NULL::numeric), -- missing_lines=4 affected_recipes=4
    ('7f13d2ce-0a51-5a35-b609-43727b2fb407'::uuid, 'Knollensellerie tiefgefroren', NULL::numeric), -- missing_lines=4 affected_recipes=4
    ('402639d7-4b96-5fe2-9eda-ba84bc020d91'::uuid, 'tomaten (passiert)', NULL::numeric), -- missing_lines=4 affected_recipes=4
    ('97166fbb-c4cf-5f8e-bb05-f25a979d4c6b'::uuid, 'Brötchen (Ciabatta)', NULL::numeric), -- missing_lines=3 affected_recipes=3
    ('e4d23a8e-0703-5054-afde-149d8a3b1de6'::uuid, 'hummus', NULL::numeric), -- missing_lines=3 affected_recipes=3
    ('57c14dc7-45d1-553d-a810-809bd56e14da'::uuid, 'kuvertüre (Zartbitter)', NULL::numeric), -- missing_lines=3 affected_recipes=3
    ('d581eed7-426c-53bb-be8d-317ef31887c4'::uuid, 'Backkakao', NULL::numeric), -- missing_lines=2 affected_recipes=2
    ('f75e88ae-1937-5ae3-a4ee-e0e7ced07f75'::uuid, 'Bohnenmix', NULL::numeric), -- missing_lines=2 affected_recipes=2
    ('e9ffdb6a-1f0a-5e8c-8582-5eac1277f34c'::uuid, 'Chiliflocken', NULL::numeric), -- missing_lines=2 affected_recipes=2
    ('81ccf129-44a0-59c0-ba8b-fda14cdcf9fb'::uuid, 'Chipotle', NULL::numeric), -- missing_lines=2 affected_recipes=2
    ('996c5138-d3ea-55e6-a80d-a6dee359498e'::uuid, 'Gurke roh', NULL::numeric), -- missing_lines=2 affected_recipes=2
    ('0ceb2ba1-a71c-5640-8766-9634278a00e8'::uuid, 'parmesan (gerieben)', NULL::numeric), -- missing_lines=2 affected_recipes=2
    ('c97c66b8-0768-58b4-a8c6-28b4fb4d7da0'::uuid, 'Sahne 10% Fett', NULL::numeric), -- missing_lines=2 affected_recipes=2
    ('79fecda5-91f8-5f59-9b7c-2123ec736617'::uuid, 'thymian (getrocknet)', NULL::numeric), -- missing_lines=2 affected_recipes=2
    ('5d20d681-97a6-5077-8e50-3d004512a7f8'::uuid, 'traubensaft', NULL::numeric), -- missing_lines=2 affected_recipes=2
    ('a831a86e-a327-59c3-bb68-ae35d6983cb6'::uuid, 'Veganer Käse', NULL::numeric), -- missing_lines=2 affected_recipes=2
    ('958ce5a2-bf88-5132-9fb8-2b7b720b8035'::uuid, 'Ananas', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('9e3c05b1-244d-51c6-a070-e5646fcd6e4d'::uuid, 'Berglinsen', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('427504d6-edc2-548b-bca4-10c74b1fd86d'::uuid, 'Blaubeeren', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('08c63bee-83ec-558e-9ab6-5d0753e756be'::uuid, 'Brezeln', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('f67542bf-eff3-58aa-9aba-0c794e43c88a'::uuid, 'Brühe (instant)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('dfa7233f-fcb7-5634-92d8-f6593cb65a45'::uuid, 'Buntes Wok-Gemüse', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('85dbbf78-afa1-5d6d-9208-1429f013acd7'::uuid, 'Chiasamen', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('5e725556-4590-5fc1-8694-603a1e92e0a3'::uuid, 'Creme Fraiche', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('29d2ae90-93b5-52df-9ed4-1b9769d1ba43'::uuid, 'Deko (Minze, Kräuter, Puderzucker, Obst)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('130a536c-a3ee-5d59-911c-240685d71b57'::uuid, 'Dr. Oetker Panna Cotta', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('ea4defef-8741-5740-a9fa-1939b9ee3989'::uuid, 'Fladenbrot', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('37d3420c-1e4a-58a5-bce8-8ca345945253'::uuid, 'Fleischbällchen Gefroren', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('9e1f0c02-21a3-597b-b200-1579651aa2af'::uuid, 'Gemüsebrühe gekörnt', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('0c9e8355-3efe-5dfe-a863-7290e513231f'::uuid, 'Gemüsebrühe (trocken)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('cb6456fc-f99f-5c50-8114-3abe0f22f38c'::uuid, 'Gnocchi roh', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('efcff82c-ec33-5775-93cb-8ee3ec5179aa'::uuid, 'Granatapfel', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('df160186-dd28-5dfc-9286-cf447e17d4da'::uuid, 'halloumi', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('8a07e83e-3d2e-505d-b4df-656ee6778528'::uuid, 'Himbeere tiefgefroren', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('eecbc83b-8438-5877-96e5-d9dfc5efb9e4'::uuid, 'kabeljau', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('36436c35-0b4c-5c1d-9946-61d7eff4e03f'::uuid, 'kardamom', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('49c0397b-2a97-5b51-b31d-ff61ee5f61c9'::uuid, 'Karotte (Mohrrübe, Möhre) roh', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('c443ff3a-4738-537e-a3b5-fe635d0ce246'::uuid, 'Käsekuchen aus Mürbeteig', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('872fb593-adf0-55a9-9301-377b7d199ee5'::uuid, 'knoblauch (getrocknet)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('89c028ba-b5f9-5d0f-bc76-e810dbb166be'::uuid, 'kokosöl', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('769a0ecb-af1a-550e-b2ea-48c5b8547e6d'::uuid, 'konfitüre (Marmelade)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('3f145cb7-4e9d-5043-857e-13498aa0ad6b'::uuid, 'Köttbullar aus Sonnenblumenprotein', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('0c27b54c-37ec-58c4-b636-ff91506f1eea'::uuid, 'kuvertüre (weiß)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('b979a032-a7bd-535b-a11d-d7f90501901f'::uuid, 'Langkorn Parboiled Wildreis', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('cfc5375f-51d3-5957-94cd-f8c162803139'::uuid, 'Limettenblätter', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('d9574835-cfac-5e9c-b66f-fbc612e4b80b'::uuid, 'Linsen-Kochbrühe', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('b2389758-8783-5f1e-b853-7d75d97c7543'::uuid, 'Linsen reif gekocht', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('4b07b6dc-c1ae-5430-aa42-1c75eea84b3e'::uuid, 'löffelbiskuits', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('05d6ff24-7dd4-5919-af28-8d735104344c'::uuid, 'mandelmilch (ungesüsst)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('431b1573-f54f-5761-bc9e-dc05da68f73f'::uuid, 'mandelmus', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('be28b1eb-d3b0-5d8c-8fc9-1c2f3a22d8cd'::uuid, 'Mangopüree', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('a08b3428-da78-5993-90fe-8f4331a1d35d'::uuid, 'Nährhefe', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('ebbf8271-6b05-5885-bb60-b9a65f5806c3'::uuid, 'Obstmischung', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('91621c2e-76c3-5682-a96b-56e1dfc3a5a8'::uuid, 'Öl', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('05f93f71-c6f1-548a-9336-913bea97f357'::uuid, 'paprika (Durchschnitt)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('3fd3970d-20f3-542b-9d0a-fca7d11fb624'::uuid, 'Pistazienmark ungezuckert', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('441a0f78-9a14-50d4-844c-ce7a018e141d'::uuid, 'Quinoa gekocht', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('37cd1afe-23fb-5575-ab93-e0eef40d02cc'::uuid, 'Ras el Hanout', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('be53f69f-f98c-56e9-ac65-27dd63263cbb'::uuid, 'Salatmix', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('f43bbe81-985c-5ad6-a00a-c0cd5ed6a080'::uuid, 'Schnittsalat (Blatt-/ Pflücksalat)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('f86416eb-c652-5fc5-8ff9-0f5569471ca6'::uuid, 'sojaflocken', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('bac37877-ad48-5480-b8c9-4d6ef7a2cda2'::uuid, 'Süßlupinenschrot', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('880e955b-aedf-5a42-9862-8f0c43ec96c0'::uuid, 'Szechuanpfeffer', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('f9bfb784-829d-5323-9fa5-6b612668b92d'::uuid, 'tofu (frisch)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('77c0524b-b0f5-5a1d-b089-a0198937bb61'::uuid, 'tomaten (stückig)', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('edb0867a-80e0-5d22-b733-3b56ca3cb735'::uuid, 'Trüffel Konzentrat', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('eed906fb-764e-5aa9-84ca-2f5ad4e0db0b'::uuid, 'Vegane Miso Butter', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('c9764079-99c4-5543-9190-332786b18cb5'::uuid, 'wassermelone', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('a5f64569-f1d1-5874-91cd-26a13f3ea160'::uuid, 'Zimtstangen / Ceylon', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('6449544e-dc42-5451-815f-dbeffc61b104'::uuid, 'Zitronengras', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('f75b4f9e-316a-52c7-8914-b4c10a9675a4'::uuid, 'zucchini', NULL::numeric), -- missing_lines=1 affected_recipes=1
    ('5325c911-3dcc-57a2-b70d-ad41278cfbee'::uuid, 'Zwiebeln roh', NULL::numeric) -- missing_lines=1 affected_recipes=1
), inserted AS (
    INSERT INTO public.ingredient_prices (
        id, ingredient_id, price_per_unit, currency, unit,
        supplier_id, supplier_name, article_number, created_at, updated_at, price_per_gram
    )
    SELECT
        gen_random_uuid(),
        p.ingredient_id,
        p.eur_per_gram,
        'EUR',
        'g',
        'manual_seed_20260317',
        'manual_seed',
        'n/a',
        NOW(),
        NOW(),
        p.eur_per_gram
    FROM price_inputs p
    WHERE p.eur_per_gram IS NOT NULL
    RETURNING ingredient_id
)
SELECT COUNT(*) AS inserted_rows FROM inserted;

COMMIT;

-- Verification
WITH latest_price AS (SELECT * FROM public.ingredient_prices_latest)
SELECT COUNT(*) AS total_recipe_lines,
       COUNT(*) FILTER (WHERE lp.price_per_gram IS NOT NULL AND ri.quantity_grams IS NOT NULL) AS priced_lines,
       COUNT(*) FILTER (WHERE lp.price_per_gram IS NULL OR ri.quantity_grams IS NULL) AS gap_lines,
       ROUND((COUNT(*) FILTER (WHERE lp.price_per_gram IS NOT NULL AND ri.quantity_grams IS NOT NULL)::numeric / NULLIF(COUNT(*),0))*100,2) AS coverage_pct
FROM recipe_ingredients ri
LEFT JOIN latest_price lp ON lp.ingredient_id = ri.ingredient_id;
