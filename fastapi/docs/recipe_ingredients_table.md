                                                Table "public.recipe_ingredients"
     Column     |           Type           | Collation | Nullable | Default | Storage  | Compression | Stats target | Description
----------------+--------------------------+-----------+----------+---------+----------+-------------+--------------+-------------
 id             | uuid                     |           | not null |         | plain    |             |              |
 created_at     | timestamp with time zone |           | not null | now()   | plain    |             |              |
 updated_at     | timestamp with time zone |           | not null | now()   | plain    |             |              |
 recipe_id      | uuid                     |           | not null |         | plain    |             |              |
 ingredient_id  | uuid                     |           | not null |         | plain    |             |              |
 quantity       | numeric(10,4)            |           |          |         | main     |             |              |
 unit           | character varying(50)    |           |          |         | extended |             |              |
 preparation    | character varying(255)   |           |          |         | extended |             |              |
 sort_order     | integer                  |           | not null | 0       | plain    |             |              |
 quid           | numeric(10,4)            |           |          |         | main     |             |              |
 item_type      | character varying(50)    |           |          |         | extended |             |              |
 quantity_grams | numeric                  |           |          |         | main     |             |              |
Indexes:
    "recipe_ingredients_pkey" PRIMARY KEY, btree (id)
    "ix_recipe_ingredients_ingredient_id" btree (ingredient_id)
    "ix_recipe_ingredients_recipe_id" btree (recipe_id)
    "ix_recipe_ingredients_sort_order" btree (sort_order)
    "uq_recipe_ingredient_order" UNIQUE CONSTRAINT, btree (recipe_id, ingredient_id, sort_order)
Check constraints:
    "recipe_ingredients_quantity_grams_non_negative" CHECK (quantity_grams IS NULL OR quantity_grams >= 0::numeric)
Foreign-key constraints:
    "recipe_ingredients_ingredient_id_fkey" FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
    "recipe_ingredients_recipe_id_fkey" FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE