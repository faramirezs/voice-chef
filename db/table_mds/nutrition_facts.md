                                             Table "public.nutrition_facts"
   Column    |  Type   | Collation | Nullable |      Default       | Storage | Compression | Stats target | Description
-------------+---------+-----------+----------+--------------------+---------+-------------+--------------+-------------
 id          | uuid    |           | not null | uuid_generate_v4() | plain   |             |              |
 energy_kj   | numeric |           |          |                    | main    |             |              |
 energy_kcal | numeric |           |          |                    | main    |             |              |
 fat         | numeric |           |          |                    | main    |             |              |
 saturates   | numeric |           |          |                    | main    |             |              |
 carbs       | numeric |           |          |                    | main    |             |              |
 sugars      | numeric |           |          |                    | main    |             |              |
 protein     | numeric |           |          |                    | main    |             |              |
 salt        | numeric |           |          |                    | main    |             |              |
Indexes:
    "nutrition_facts_pkey" PRIMARY KEY, btree (id)
Referenced by:
    TABLE "recipe_nutrition" CONSTRAINT "recipe_nutrition_nutrition_id_fkey" FOREIGN KEY (nutrition_id) REFERENCES nutrition_facts(id) ON DELETE CASCADE