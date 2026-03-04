## Start Docker

```bash
open -a Docker
```

## To dump database

```bash
docker run --rm postgres:17.8 pg_dump \
  --no-owner --no-acl --inserts \
  "postgresql://neondb_owner:npg_sfGtpBNm13gy@ep-quiet-rice-alh540v4-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require" \
  > db/init/01_dump.sql
```

In case we want to have only data or only schema we could use these flags:

```bash
--schema-only	#Only CREATE TABLE, indexes...	Sharing structure without sensitive data
--data-only	#Only INSERT/COPY rows	When schema already exists on target
```

```bash
docker compose down -v   # destroys the volume
docker compose up        # fresh start, runs 00_ then 01_ for db sql scripts

```


To "ping" postgres
```bash
docker run --rm postgres:17.8 pg_isready -h localhost -p 5432 -U recipe_user
```

```bash
psql -U recipe_user -d recipe_db -c "SELECT * FROM recipes WHERE name ILIKE '%curry%';"
```
