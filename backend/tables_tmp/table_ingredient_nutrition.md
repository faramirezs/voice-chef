                         Table "public.ingredient_nutrition"
    Column     |           Type           | Collation | Nullable |      Default
---------------+--------------------------+-----------+----------+-------------------
 id            | uuid                     |           | not null | gen_random_uuid()
 ingredient_id | uuid                     |           | not null |
 energy_kj     | numeric(10,2)            |           |          |
 energy_kcal   | numeric(10,2)            |           |          |
 carbs         | numeric(10,2)            |           |          |
 protein       | numeric(10,2)            |           |          |
 fat           | numeric(10,2)            |           |          |
 sugars        | numeric(10,2)            |           |          |
 fiber         | numeric(10,2)            |           |          |
 saturates     | numeric(10,2)            |           |          |
 salt          | numeric(10,2)            |           |          |
 created_at    | timestamp with time zone |           |          | now()
 updated_at    | timestamp with time zone |           |          | now()
 alcohol       | numeric(10,3)            |           |          |
 water         | numeric(10,3)            |           |          |
Indexes:
    "ingredient_nutrition_pkey" PRIMARY KEY, btree (id)
    "ingredient_nutrition_ingredient_id_key" UNIQUE CONSTRAINT, btree (ingredient_id)
Foreign-key constraints:
    "ingredient_nutrition_ingredient_id_fkey" FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE