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
docker exec -it voice-chef-db-1 pg_isready -h localhost -p 5432 -U recipe_user
```
Or inside the container

```bash
psql -U recipe_user -d recipe_db -c "SELECT * FROM recipes WHERE name ILIKE '%curry%';"
```

## Fontend

Development — just this, override.yml is auto-merged

```bash
docker compose up
```

Production — explicitly load the prod file

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Vite boilerplate:
This gives us Vite's dev server (powered by ESBuild), HMR out of the box, and TypeScript support:

```bash
npm create vite@latest my-app -- --template react-ts
```

```bash
npm install react-router-dom @tanstack/react-query axios
```

### Build and run the frontend app:
```bash
docker build --target dev -t recipes-frontend:dev
```
```bash
docker run -p 5173:5173 recipes-frontend:dev
```

**What if we want hot-reload?**
Mount volumes:
```bash
docker run -p 5173:5173 \
  -v "$(pwd)":/frontend \
  -v /frontend/node_modules \
  recipes-frontend:dev
```



```bash
docker build --target builder \
  --build-arg VITE_API_URL=http://api:5173 \
  -t recipes-frontend:builder .
```

Inspect build output
```bash
docker run --rm recipes-frontend:builder ls -lh /app/dist
```

Build and run production image:
```bash
# Build
docker build --target runtime -t recipes-frontend:prod .
docker build --no-cache --target runtime -t recipes-frontend:prod .
# --no-cache forces Docker to re-run every layer, including your new chown commands.

# Run
docker run -p 8080:80 recipes-frontend:prod

```

Comparing Docker images for frontend:

```bash
docker images recipes-frontend
#Returns:
REPOSITORY         TAG       IMAGE ID       CREATED             SIZE
recipes-frontend   prod      4000e83b05bc   4 minutes ago       92.1MB
recipes-frontend   builder   1ca82a22683c   10 minutes ago      1.08GB
recipes-frontend   dev       268109152cf7   About an hour ago   1.07GB
recipes-frontend   deps      7c177777c34c   3 hours ago         303MB
```
