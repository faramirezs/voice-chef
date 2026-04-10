## Docker Compose Workflows

### Development
This setup uses the `dev` stage of the Dockerfile (Vite with Hot Module Replacement).

```bash
make dev
```

### Production (Local Test)
To test the production build (Nginx serving static files) locally, run the base file **without** the override:

```bash
make prod
```

To display states of containers, volumes and network
```bash
make status
```
To stop the application and remove containers and images
```bash
make clean
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

## How to activate the virtual environment for Python

```bash
# If your virtual environment is named ".venv"
source .venv/bin/activate
```
