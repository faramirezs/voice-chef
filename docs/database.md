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
