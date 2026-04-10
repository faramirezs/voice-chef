                                                     Table "public.ingredient_units"
     Column     |          Type          | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description
----------------+------------------------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id             | uuid                   |           | not null | gen_random_uuid() | plain    |             |              |
 ingredient_id  | uuid                   |           | not null |                   | plain    |             |              |
 unit_code      | character varying(20)  |           | not null |                   | extended |             |              |
 grams_per_unit | numeric                |           | not null |                   | main     |             |              |
 label          | character varying(100) |           |          |                   | extended |             |              |
Indexes:
    "ingredient_units_pkey" PRIMARY KEY, btree (id)
    "idx_ingredient_units_ingredient" btree (ingredient_id)
    "uq_ingredient_unit" UNIQUE CONSTRAINT, btree (ingredient_id, unit_code)
Check constraints:
    "ingredient_units_grams_per_unit_positive" CHECK (grams_per_unit > 0::numeric)
Foreign-key constraints:
    "ingredient_units_ingredient_id_fkey" FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE