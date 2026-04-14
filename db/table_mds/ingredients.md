                                                     Table "public.ingredients"
      Column       |           Type           | Collation | Nullable | Default | Storage  | Compression | Stats target | Description
-------------------+--------------------------+-----------+----------+---------+----------+-------------+--------------+-------------
 id                | uuid                     |           | not null |         | plain    |             |              |
 created_at        | timestamp with time zone |           | not null | now()   | plain    |             |              |
 updated_at        | timestamp with time zone |           | not null | now()   | plain    |             |              |
 tenant_id         | uuid                     |           |          |         | plain    |             |              |
 name              | character varying(255)   |           | not null |         | extended |             |              |
 default_unit      | character varying(50)    |           |          |         | extended |             |              |
 nutrition_id      | uuid                     |           |          |         | plain    |             |              |
 usage_count       | integer                  |           |          | 0       | plain    |             |              |
 recipe_count      | integer                  |           |          | 0       | plain    |             |              |
 ingredient_type   | character varying(50)    |           |          |         | extended |             |              |
 bls_key           | character varying(100)   |           |          |         | extended |             |              |
 is_custom         | boolean                  |           |          | false   | plain    |             |              |
 has_parent        | boolean                  |           |          | false   | plain    |             |              |
 parent_id         | uuid                     |           |          |         | plain    |             |              |
 initial_recipe_id | uuid                     |           |          |         | plain    |             |              |
Indexes:
    "ingredients_pkey" PRIMARY KEY, btree (id)
    "idx_ingredients_parent_id" btree (parent_id)
    "idx_ingredients_usage_count" btree (usage_count)
    "ix_ingredients_name" btree (name)
Foreign-key constraints:
    "ingredients_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES ingredients(id)
    "ingredients_tenant_id_fkey" FOREIGN KEY (tenant_id) REFERENCES tenants(id)
Referenced by:
    TABLE "ingredient_nutrition" CONSTRAINT "ingredient_nutrition_ingredient_id_fkey" FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
    TABLE "ingredient_prices" CONSTRAINT "ingredient_prices_ingredient_id_fkey" FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
    TABLE "ingredient_units" CONSTRAINT "ingredient_units_ingredient_id_fkey" FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
    TABLE "ingredients" CONSTRAINT "ingredients_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES ingredients(id)
    TABLE "recipe_ingredients" CONSTRAINT "recipe_ingredients_ingredient_id_fkey" FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE