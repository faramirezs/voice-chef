                                                      Table "public.recipe_photos"
   Column   |           Type           | Collation | Nullable |      Default       | Storage  | Compression | Stats target | Description
------------+--------------------------+-----------+----------+--------------------+----------+-------------+--------------+-------------
 id         | uuid                     |           | not null | uuid_generate_v4() | plain    |             |              |
 recipe_id  | uuid                     |           | not null |                    | plain    |             |              |
 photo_url  | text                     |           |          |                    | extended |             |              |
 photo_data | bytea                    |           |          |                    | extended |             |              |
 photo_type | character varying(50)    |           |          |                    | extended |             |              |
 is_primary | boolean                  |           |          | false              | plain    |             |              |
 created_at | timestamp with time zone |           |          | now()              | plain    |             |              |
Indexes:
    "recipe_photos_pkey" PRIMARY KEY, btree (id)
    "idx_recipe_photos_recipe" btree (recipe_id)
Foreign-key constraints:
    "recipe_photos_recipe_id_fkey" FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE