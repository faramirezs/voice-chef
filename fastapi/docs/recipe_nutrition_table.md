                                                Table "public.recipe_nutrition"
    Column    |           Type           | Collation | Nullable | Default | Storage | Compression | Stats target | Description
--------------+--------------------------+-----------+----------+---------+---------+-------------+--------------+-------------
 recipe_id    | uuid                     |           | not null |         | plain   |             |              |
 nutrition_id | uuid                     |           |          |         | plain   |             |              |
 updated_at   | timestamp with time zone |           |          | now()   | plain   |             |              |
Indexes:
    "recipe_nutrition_pkey" PRIMARY KEY, btree (recipe_id)
    "idx_recipe_nutrition_nutrition" btree (nutrition_id)
Foreign-key constraints:
    "recipe_nutrition_nutrition_id_fkey" FOREIGN KEY (nutrition_id) REFERENCES nutrition_facts(id) ON DELETE CASCADE
Triggers:
    update_recipe_nutrition_updated_at BEFORE UPDATE ON recipe_nutrition FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()