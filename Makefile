COMPOSE = docker compose
PROD_FILE = docker-compose.yml
DEV_FILE = docker-compose.override.yml

ENV = .env

all: up

$(ENV): .env.example
	@if [ -e "$(ENV)" ]; then \
		echo "Error: $(ENV) already exists; refusing to overwrite existing environment configuration."; \
		echo "If you want to regenerate it from .env.example, delete $(ENV) first."; \
		exit 1; \
	else \
		cp .env.example "$(ENV)"; \
	fi

build: $(ENV)
	$(COMPOSE) build

up: $(ENV)
	$(COMPOSE) up --build --detach

prod: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) up --build --detach

dev: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up --build --detach

down:
	$(COMPOSE) down

start:
	$(COMPOSE) start

stop:
	$(COMPOSE) stop

show:
	@$(COMPOSE) ps -a
	@printf '\n'
	@docker volume ls
	@printf '\n'
	@docker network ls
	@printf '\n'
# 	@docker images
#  	@printf '\n'

logs:
	$(COMPOSE) logs

ps:
	$(COMPOSE) ps -a

clean:
	$(COMPOSE) down --rmi all

re: clean all

fclean: clean
	$(COMPOSE) down --rmi all -v --remove-orphans
	docker volume prune
	rm -f .env


HELP_TEXT =
"Available commands:\n"
	" make build → Build containers"
	" make up → Start (default)"
	" make prod → Start in production mode"
	" make dev → Start in development mode"
	" make down → Stop and remove containers"
	" make start → Start existing containers"
	" make stop → Stop containers"
	" make logs → Show logs"
	" make ps → List containers"
	" make show → Full Docker state"
	" make clean → Remove containers + images"
	" make fclean → Full cleanup (volumes + env)\n"

help:
	@echo ""
	@printf "%b\n" $(HELP_TEXT)

%:
	@echo "❌ Unknown command: '$@'"
	@echo ""
	@printf "%b\n" $(HELP_TEXT)
	@EXIT 1

.PHONY: all build up prod dev down re stop start show logs ps clean fclean