                                     Table "public.users"
    Column     |           Type           | Collation | Nullable |           Default
---------------+--------------------------+-----------+----------+-----------------------------
 id            | uuid                     |           | not null |
 created_at    | timestamp with time zone |           | not null | now()
 updated_at    | timestamp with time zone |           | not null | now()
 email         | character varying(255)   |           | not null |
 password_hash | character varying(255)   |           | not null |
 role          | character varying(50)    |           | not null | 'editor'::character varying
 is_active     | boolean                  |           | not null | true
 tenant_id     | uuid                     |           |          |
Indexes:
    "users_pkey" PRIMARY KEY, btree (id)
    "ix_users_email" UNIQUE, btree (email)
    "users_email_key" UNIQUE CONSTRAINT, btree (email)
Foreign-key constraints:
    "users_tenant_id_fkey" FOREIGN KEY (tenant_id) REFERENCES tenants(id)
Referenced by:
    TABLE "recipes" CONSTRAINT "recipes_created_by_fkey" FOREIGN KEY (created_by) REFERENCES users(id)