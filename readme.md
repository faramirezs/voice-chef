## Start Docker

```bash
open -a Docker
```

## Docker Compose Workflows

### Development
By default, Docker Compose auto-merges `docker-compose.yml` and `docker-compose.override.yml`. This setup uses the `dev` stage of the Dockerfile (Vite with Hot Module Replacement).

```bash
docker compose up --build
```

### Production (Local Test)
To test the production build (Nginx serving static files) locally, run the base file **without** the override:

```bash
docker compose -f docker-compose.yml up --build
```

---
