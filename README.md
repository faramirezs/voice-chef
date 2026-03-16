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

### Useful comands and debug commands

### Start Docker

```bash
open -a Docker
```

### LOGS

To see what's happening "under the hood" of any service, view the logs in real time:
```bash
docker compose logs -f [service_name]
```

#### Fix the port conflict

For example, a port for DB. Make sure no other service is using port 5432 on your host.

```bash
sudo lsof -i :5432
```

Another example: nginx port

Check if you have a local nginx running:

```bash
sudo lsof -i :80
# check if nginx is running (outside Docker)
sudo systemctl status nginx
# If you want to stop nginx on your host
sudo systemctl stop nginx
```
