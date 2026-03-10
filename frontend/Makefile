build-dev:
	docker build --target dev -t recipes-frontend:dev .

build-prod:
	docker build --target runtime -t recipes-frontend:prod .

run-dev:
	docker run -p 5173:5173 -v $(PWD):/app -v /app/node_modules recipes-frontend:dev

run-prod:
	docker run -p 8080:80 recipes-frontend:prod
