## Start Docker

```bash
open -a Docker
```


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
# --no-cache forces Docker to re-run every layer

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
