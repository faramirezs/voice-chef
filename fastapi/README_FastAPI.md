## Start Docker

```bash
open -a Docker
```
## 
```bash
docker compose build      # to build images takes place in compose file
docker compose up         # to run the fastapi and postgress containers
docker compose down       # shutdown the fastapi and postgress
docker compose down -v    # shutdown the fastapi and postgress
```



## To dump database

```bash
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

```bash
docker compose down -v   # destroys the volume
docker compose up        # fresh start, runs 00_ then 01_ for db sql scripts
```

To "ping" postgres
```bash
docker exec -it voice-chef-db-1 pg_isready -h localhost -p 5432 -U recipe_user
```
Or inside the container

```bash
psql -U recipe_user -d recipe_db -c "SELECT * FROM recipes WHERE name ILIKE '%curry%';"
```

## Packages/Extensions

Uvicorn: Uvicorn is an ASGI web server implementation for Python.
Uvicorn currently supports HTTP/1.1 and WebSockets.

Pydantic: Pydantic is the most widely used data validation library for Python.

Psycog: PostgreSQL database adapter/driver for Python.
Its main features are the complete implementation of the Python DB API 2.0 specification and the thread safety (several threads can share the same connection). It was designed for heavily multi-threaded applications that create and destroy lots of cursors and make a large number of concurrent INSERTs or UPDATEs.

SQLAlchemy: Python SQL toolkit and Object Relational Mapper
Povides the data mapper pattern, where classes can be mapped to the database in open ended, multiple ways - allowing the object model and database schema to develop in a cleanly decoupled way from the beginning.

# sqlacodegen_v2 = scan database to create the SQLAlchemy model
docker compose exec fastapi sqlacodegen_v2 postgresql+psycopg://recipe_user:recipe_pass123@db:5432/recipe_db --generator sqlmodels > models.py