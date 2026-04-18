# Data base

## What is the dump file `db/init/01_dump.sql`

We build our DB this way: 

**empty DB → run 01_dump.sql → → alembic checks db version, then if versions is not head it run migrations until head → ready DB**

The system is designed to be resilient and bring the database up to the latest version automatically so a developer can start working.

## CI Schema Drift Checks (Test)

More details about the test can be found in the [`Dump safety and regeneration`](migrations.md#dump-safety-and-regeneration) section of the migrations document.

The CI jobs in `.github/workflows/schema-drift.yml` independently check for schema drift against the current SQLAlchemy models defined in the Python code.

1. **Migration path**

The `schema-drift` job builds the DB from scratch using migrations (`alembic upgrade head`) and then checks for drift.

**empty DB → run all migrations → DONE**

2. The **Dump path**

The `schema-drift-dump-compat` job builds the DB from 01_dump.sql and then checks for drift.

**empty DB → load dump → DONE**

If either job detects drift, it means the schema source for that path (either the migrations or the dump file) is out of sync with the application models.

**The rule to pass CI test**: Dump alone must already represent the latest schema.

The dump (`db/init/01_dump.sql`) **must be kept up-to-date with the latest schema**. Even though migrations exist, the dump is treated as a canonical snapshot of the current schema.

**After adding a migration, you need to:**

1. Run migrations locally to apply the changes.
2. Export a fresh dump from the migrated database. 
3. Replace `db/init/01_dump.sql`.

 It intentionally does not run `alembic upgrade head` because its purpose is to test the dump file itself. If the dump is not updated, CI checks will fail.

---

## To dump database

```bash
 # DATABASE_URL should contain your full Postgres/Neon connection string, e.g.:
 # export DATABASE_URL="postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require&channel_binding=require"
docker run --rm postgres:17.8 pg_dump \
  --no-owner --no-acl --inserts \
  "$DATABASE_URL" \
  > db/init/01_dump.sql
```

In case we want to have only data or only schema we could use these flags:

```bash
--schema-only	#Only CREATE TABLE, indexes...	Sharing structure without sensitive data
--data-only	#Only INSERT/COPY rows	When schema already exists on target
```

## Export local schema named by Alembic version

After a fresh start/migration, export only schema and include current Alembic revision in the filename:

```bash
REV=$(docker compose exec -T db psql -X -A -t -P pager=off -U recipe_user -d recipe_db -c "SELECT version_num FROM public.alembic_version;") && \
OUT="db/schema_alembic_${REV}.sql" && \
docker compose exec -T db pg_dump -U recipe_user -d recipe_db --schema-only --no-owner --no-privileges > "$OUT" && \
echo "Created $OUT"
```

```bash
docker compose down -v   # destroys the volume
docker compose up        # fresh start, runs 00_ then 01_ for db sql scripts
```

To "ping" postgres
```bash
docker exec -it voice_chef-db-1 pg_isready -h localhost -p 5432 -U recipe_user
```
Or inside the container

```bash
psql -U recipe_user -d recipe_db -c "SELECT * FROM recipes WHERE name ILIKE '%curry%';"
```
