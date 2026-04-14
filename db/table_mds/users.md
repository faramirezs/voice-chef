                                                                Table "public.users"
    Column     |           Type           | Collation | Nullable |           Default           | Storage  | Compression | Stats target | Description
---------------+--------------------------+-----------+----------+-----------------------------+----------+-------------+--------------+-------------
 id            | uuid                     |           | not null |                             | plain    |             |              |
 created_at    | timestamp with time zone |           | not null | now()                       | plain    |             |              |
 updated_at    | timestamp with time zone |           | not null | now()                       | plain    |             |              |
 email         | character varying(255)   |           | not null |                             | extended |             |              |
 password_hash | character varying(255)   |           | not null |                             | extended |             |              |
 role          | character varying(50)    |           | not null | 'editor'::character varying | extended |             |              |
 is_active     | boolean                  |           | not null | true                        | plain    |             |              |
 tenant_id     | uuid                     |           |          |                             | plain    |             |              |
Indexes:
    "users_pkey" PRIMARY KEY, btree (id)
    "ix_users_email" UNIQUE, btree (email)
    "users_email_key" UNIQUE CONSTRAINT, btree (email)
Foreign-key constraints:
    "users_tenant_id_fkey" FOREIGN KEY (tenant_id) REFERENCES tenants(id)
Referenced by:
    TABLE "recipes" CONSTRAINT "recipes_created_by_fkey" FOREIGN KEY (created_by) REFERENCES users(id)