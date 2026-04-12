                                                   Table "public.ingredient_nutrition"
    Column     |           Type           | Collation | Nullable |      Default      | Storage | Compression | Stats target | Description
---------------+--------------------------+-----------+----------+-------------------+---------+-------------+--------------+-------------
 id            | uuid                     |           | not null | gen_random_uuid() | plain   |             |              |
 ingredient_id | uuid                     |           | not null |                   | plain   |             |              |
 energy_kj     | numeric(10,2)            |           |          |                   | main    |             |              |
 energy_kcal   | numeric(10,2)            |           |          |                   | main    |             |              |
 carbs         | numeric(10,2)            |           |          |                   | main    |             |              |
 protein       | numeric(10,2)            |           |          |                   | main    |             |              |
 fat           | numeric(10,2)            |           |          |                   | main    |             |              |
 sugars        | numeric(10,2)            |           |          |                   | main    |             |              |
 fiber         | numeric(10,2)            |           |          |                   | main    |             |              |
 saturates     | numeric(10,2)            |           |          |                   | main    |             |              |
 salt          | numeric(10,2)            |           |          |                   | main    |             |              |
 created_at    | timestamp with time zone |           |          | now()             | plain   |             |              |
 updated_at    | timestamp with time zone |           |          | now()             | plain   |             |              |
 alcohol       | numeric(10,3)            |           |          |                   | main    |             |              |
 water         | numeric(10,3)            |           |          |                   | main    |             |              |
Indexes:
    "ingredient_nutrition_pkey" PRIMARY KEY, btree (id)
    "ingredient_nutrition_ingredient_id_key" UNIQUE CONSTRAINT, btree (ingredient_id)
Foreign-key constraints:
    "ingredient_nutrition_ingredient_id_fkey" FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
Access method: heap