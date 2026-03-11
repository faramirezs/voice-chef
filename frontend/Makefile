build-dev:
	docker build --target dev -t recipes-frontend:dev .
# builds only the dev stage (Node + source code + npm run dev) for local development.

run-dev:
	docker run -p 5173:5173 -v "$(PWD):/app" -v /app/node_modules recipes-frontend:dev
# starts Vite dev server, maps host port 5173, mounts your current folder into container for live reload, and keeps container node_modules isolated.

build-prod:
	docker build --target runtime -t recipes-frontend:prod .
# executes full prod pipeline (builder creates dist, runtime serves it with Nginx).

run-prod:
	docker run -p 8080:80 recipes-frontend:prod
# runs docker run -p 8080:80 recipes-frontend:prod; serves built static app on http://localhost:8080.
