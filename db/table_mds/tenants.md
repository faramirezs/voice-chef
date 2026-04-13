                                                    Table "public.tenants"
   Column   |           Type           | Collation | Nullable | Default | Storage  | Compression | Stats target | Description
------------+--------------------------+-----------+----------+---------+----------+-------------+--------------+-------------
 id         | uuid                     |           | not null |         | plain    |             |              |
 created_at | timestamp with time zone |           | not null | now()   | plain    |             |              |
 updated_at | timestamp with time zone |           | not null | now()   | plain    |             |              |
 name       | character varying(255)   |           | not null |         | extended |             |              |
 slug       | character varying(100)   |           | not null |         | extended |             |              |
 is_active  | boolean                  |           | not null | true    | plain    |             |              |
 settings   | character varying        |           |          |         | extended |             |              |
Indexes:
    "tenants_pkey" PRIMARY KEY, btree (id)
    "ix_tenants_name" btree (name)
    "ix_tenants_slug" UNIQUE, btree (slug)
    "tenants_slug_key" UNIQUE CONSTRAINT, btree (slug)
Referenced by:
    TABLE "ingredients" CONSTRAINT "ingredients_tenant_id_fkey" FOREIGN KEY (tenant_id) REFERENCES tenants(id)
    TABLE "recipes" CONSTRAINT "recipes_tenant_id_fkey" FOREIGN KEY (tenant_id) REFERENCES tenants(id)
    TABLE "users" CONSTRAINT "users_tenant_id_fkey" FOREIGN KEY (tenant_id) REFERENCES tenants(id)