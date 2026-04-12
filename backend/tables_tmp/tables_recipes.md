                                          Table "public.recipes"
          Column           |           Type           | Collation | Nullable |          Default
---------------------------+--------------------------+-----------+----------+----------------------------
 id                        | uuid                     |           | not null |
 created_at                | timestamp with time zone |           | not null | now()
 updated_at                | timestamp with time zone |           | not null | now()
 tenant_id                 | uuid                     |           |          |
 name                      | character varying(255)   |           | not null |
 description               | text                     |           |          |
 yield_amount              | numeric(10,2)            |           |          |
 yield_unit                | character varying(50)    |           |          |
 instructions              | text                     |           |          |
 status                    | character varying(50)    |           | not null | 'draft'::character varying
 created_by                | uuid                     |           |          |
 description_short         | text                     |           |          |
 serving_recommendation    | text                     |           |          |
 side_dishes               | text                     |           |          |
 notes                     | text                     |           |          |
 preparation_time          | text                     |           |          |
 waiting_time              | text                     |           |          |
 cooking_time              | text                     |           |          |
 shelf_life                | text                     |           |          |
 reduction_factor          | numeric(10,4)            |           |          |
 eigene_menge              | numeric(10,2)            |           |          |
 recipe_number             | character varying(100)   |           |          |
 packaging                 | text                     |           |          |
 packaging_material        | text                     |           |          |
 net_weight                | numeric(10,2)            |           |          |
 fill_weight               | numeric(10,2)            |           |          |
 fill_quantity             | numeric(10,2)            |           |          |
 drained_weight            | numeric(10,2)            |           |          |
 total_weight              | numeric(10,2)            |           |          |
 portion_by_weight         | boolean                  |           |          | false
 portion_weight            | numeric(10,2)            |           |          |
 batch_number              | character varying(100)   |           |          |
 production_date           | date                     |           |          |
 use_by_date               | date                     |           |          |
expiry_date               | date                     |           |          |
 storage_text              | text                     |           |          |
 storage_temperature       | character varying(50)    |           |          |
 origin_fish               | text                     |           |          |
 origin_location           | text                     |           |          |
 devices                   | text                     |           |          |
 utensils                  | text                     |           |          |
 labor_effort              | character varying(50)    |           |          |
 margin                    | numeric(10,2)            |           |          |
 nutri_score_category      | character varying(10)    |           |          |
 nutri_score_veg_fruits    | numeric(5,2)             |           |          |
 mise_en_place_display     | boolean                  |           |          | true
 notes_instructions        | text                     |           |          |
 is_component              | boolean                  |           |          | false
 ingredient_list_custom    | text                     |           |          |
 allergene_source          | text                     |           |          |
 unit_measure              | character varying(50)    |           |          |
 unit_serving              | character varying(50)    |           |          |
 preference_nutri_value    | numeric(10,2)            |           |          |
 yield_mode                | character varying(20)    |           | not null | 'count'::character varying
 portion_size_grams        | numeric                  |           |          |
 total_raw_weight_grams    | numeric                  |           |          |
 total_cooked_weight_grams | numeric                  |           |          |
 portions_count_resolved   | numeric                  |           |          |
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