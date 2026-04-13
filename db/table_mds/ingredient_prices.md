                                                         Table "public.ingredient_prices"
     Column     |           Type           | Collation | Nullable |         Default          | Storage  | Compression | Stats target | Description
----------------+--------------------------+-----------+----------+--------------------------+----------+-------------+--------------+-------------
 id             | uuid                     |           | not null | uuid_generate_v4()       | plain    |             |              |
 ingredient_id  | uuid                     |           | not null |                          | plain    |             |              |
 price_per_unit | numeric(10,2)            |           |          |                          | main     |             |              |
 currency       | character varying(3)     |           |          | 'EUR'::character varying | extended |             |              |
 unit           | character varying(50)    |           |          |                          | extended |             |              |
 supplier_id    | character varying(100)   |           |          |                          | extended |             |              |
 supplier_name  | character varying(255)   |           |          |                          | extended |             |              |
 article_number | character varying(100)   |           |          |                          | extended |             |              |
 created_at     | timestamp with time zone |           |          | now()                    | plain    |             |              |
 updated_at     | timestamp with time zone |           |          | now()                    | plain    |             |              |
 price_per_gram | numeric(14,8)            |           |          |                          | main     |             |              |
Indexes:
    "ingredient_prices_pkey" PRIMARY KEY, btree (id)
    "idx_ingredient_prices_ingredient" btree (ingredient_id)
    "idx_ingredient_prices_latest_lookup" btree (ingredient_id, unit, updated_at DESC, created_at DESC, id DESC)
    "ingredient_prices_ingredient_id_supplier_id_key" UNIQUE CONSTRAINT, btree (ingredient_id, supplier_id)
Check constraints:
    "ingredient_prices_price_per_gram_positive" CHECK (price_per_gram IS NULL OR price_per_gram > 0::numeric)
Foreign-key constraints:
    "ingredient_prices_ingredient_id_fkey" FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE