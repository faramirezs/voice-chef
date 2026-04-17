                                                                      Table "public.recipes"
          Column           |           Type           | Collation | Nullable |          Default           | Storage  | Compression | Stats target | Description
---------------------------+--------------------------+-----------+----------+----------------------------+----------+-------------+--------------+-------------
 id                        | uuid                     |           | not null |                            | plain    |             |              |
 created_at                | timestamp with time zone |           | not null | now()                      | plain    |             |              |
 updated_at                | timestamp with time zone |           | not null | now()                      | plain    |             |              |
 tenant_id                 | uuid                     |           |          |                            | plain    |             |              |
 name                      | character varying(255)   |           | not null |                            | extended |             |              |
 description               | text                     |           |          |                            | extended |             |              |
 yield_amount              | numeric(10,2)            |           |          |                            | main     |             |              |
 yield_unit                | character varying(50)    |           |          |                            | extended |             |              |
 instructions              | text                     |           |          |                            | extended |             |              |
 status                    | character varying(50)    |           | not null | 'draft'::character varying | extended |             |              |
 created_by                | uuid                     |           |          |                            | plain    |             |              |
 description_short         | text                     |           |          |                            | extended |             |              |
 serving_recommendation    | text                     |           |          |                            | extended |             |              |
 side_dishes               | text                     |           |          |                            | extended |             |              |
 notes                     | text                     |           |          |                            | extended |             |              |
 preparation_time          | text                     |           |          |                            | extended |             |              |
 waiting_time              | text                     |           |          |                            | extended |             |              |
 cooking_time              | text                     |           |          |                            | extended |             |              |
 shelf_life                | text                     |           |          |                            | extended |             |              |
 reduction_factor          | numeric(10,4)            |           |          |                            | main     |             |              |
 eigene_menge              | numeric(10,2)            |           |          |                            | main     |             |              |
 recipe_number             | character varying(100)   |           |          |                            | extended |             |              |
 packaging                 | text                     |           |          |                            | extended |             |              |
 packaging_material        | text                     |           |          |                            | extended |             |              |
 net_weight                | numeric(10,2)            |           |          |                            | main     |             |              |
 fill_weight               | numeric(10,2)            |           |          |                            | main     |             |              |
 fill_quantity             | numeric(10,2)            |           |          |                            | main     |             |              |
 drained_weight            | numeric(10,2)            |           |          |                            | main     |             |              |
 total_weight              | numeric(10,2)            |           |          |                            | main     |             |              |
 portion_by_weight         | boolean                  |           |          | false                      | plain    |             |              |
 portion_weight            | numeric(10,2)            |           |          |                            | main     |             |              |
 batch_number              | character varying(100)   |           |          |                            | extended |             |              |
 production_date           | date                     |           |          |                            | plain    |             |              |
 use_by_date               | date                     |           |          |                            | plain    |             |              |
 expiry_date               | date                     |           |          |                            | plain    |             |              |
 storage_text              | text                     |           |          |                            | extended |             |              |
 storage_temperature       | character varying(50)    |           |          |                            | extended |             |              |
 origin_fish               | text                     |           |          |                            | extended |             |              |
 origin_location           | text                     |           |          |                            | extended |             |              |
 devices                   | text                     |           |          |                            | extended |             |              |
 utensils                  | text                     |           |          |                            | extended |             |              |
 labor_effort              | character varying(50)    |           |          |                            | extended |             |              |
 margin                    | numeric(10,2)            |           |          |                            | main     |             |              |
 nutri_score_category      | character varying(10)    |           |          |                            | extended |             |              |
 nutri_score_veg_fruits    | numeric(5,2)             |           |          |                            | main     |             |              |
 mise_en_place_display     | boolean                  |           |          | true                       | plain    |             |              |
 notes_instructions        | text                     |           |          |                            | extended |             |              |
 is_component              | boolean                  |           |          | false                      | plain    |             |              |
 ingredient_list_custom    | text                     |           |          |                            | extended |             |              |
 allergene_source          | text                     |           |          |                            | extended |             |              |
 unit_measure              | character varying(50)    |           |          |                            | extended |             |              |
 unit_serving              | character varying(50)    |           |          |                            | extended |             |              |
 preference_nutri_value    | numeric(10,2)            |           |          |                            | main     |             |              |
 yield_mode                | character varying(20)    |           | not null | 'count'::character varying | extended |             |              |
 portion_size_grams        | numeric                  |           |          |                            | main     |             |              |
 total_raw_weight_grams    | numeric                  |           |          |                            | main     |             |              |
 total_cooked_weight_grams | numeric                  |           |          |                            | main     |             |              |
 portions_count_resolved   | numeric                  |           |          |                            | main     |             |              |
Indexes:
    "recipes_pkey" PRIMARY KEY, btree (id)
    "idx_recipes_batch_number" btree (batch_number)
    "idx_recipes_is_component" btree (is_component)
    "idx_recipes_reduction_factor" btree (reduction_factor)
    "idx_recipes_yield_mode" btree (yield_mode)
    "ix_recipes_name" btree (name)
Check constraints:
    "positive_portion_size_grams" CHECK (portion_size_grams IS NULL OR portion_size_grams > 0::numeric)
    "positive_portions_count_resolved" CHECK (portions_count_resolved IS NULL OR portions_count_resolved > 0::numeric)
    "positive_total_cooked_weight_grams" CHECK (total_cooked_weight_grams IS NULL OR total_cooked_weight_grams >= 0::numeric)
    "positive_total_raw_weight_grams" CHECK (total_raw_weight_grams IS NULL OR total_raw_weight_grams >= 0::numeric)
    "valid_yield_mode" CHECK (yield_mode::text = ANY (ARRAY['count'::character varying, 'weight'::character varying]::text[]))
    "weight_mode_requires_portion_size_when_active" CHECK (status::text <> 'active'::text OR yield_mode::text <> 'weight'::text OR portion_size_grams IS NOT NULL AND portion_size_grams > 0::numeric)
Foreign-key constraints:
    "recipes_created_by_fkey" FOREIGN KEY (created_by) REFERENCES users(id)
    "recipes_tenant_id_fkey" FOREIGN KEY (tenant_id) REFERENCES tenants(id)
Referenced by:
    TABLE "recipe_ingredients" CONSTRAINT "recipe_ingredients_recipe_id_fkey" FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
    TABLE "recipe_photos" CONSTRAINT "recipe_photos_recipe_id_fkey" FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE