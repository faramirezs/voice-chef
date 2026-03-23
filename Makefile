COMPOSE = docker compose
PROD_FILE = docker-compose.yml
DEV_FILE = docker-compose.override.yml

ENV = .env

all: help

$(ENV): .env.example

	@if [ -e "$(ENV)" ]; then \
		echo 'Error: $(ENV) already exists; refusing to overwrite existing environment configuration.'; \
		echo "If you want to regenerate it from .env.example, check both files to see if you have any local changes."; \
		echo "If there are any then copy those changes to .env.example first and delete $(ENV)."; \
		exit 1; \
	else \
		cp .env.example "$(ENV)"; \
	fi

dev: $(ENV)
	@echo "Building in dev_mode"
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up --build --detach
	@echo "VOICE-CHEF is running in dev_mode"

prod: $(ENV)
	@echo "Building in prod_mode"
	$(COMPOSE) -f $(PROD_FILE) up --build --detach
	@echo "VOICE-CHEF is running in prod_mode"
	
# build: $(ENV)
# 	$(COMPOSE) build

# up: dev
# 	$(COMPOSE) up --build --detach

# start: $(ENV)
# 	$(COMPOSE) start

# stop:
# 	$(COMPOSE) stop

down:
	$(COMPOSE) down

clean:
	@echo "Stopping the containers and removing them along with the images..."
	$(COMPOSE) down --rmi all

fclean: clean
	@echo "Removing the volumes..."
	$(COMPOSE) down -v --remove-orphans
	docker volume prune

re: clean dev

show:
	@printf 'CONTAINERS:\n'
	@$(COMPOSE) ps -a
	@printf '\n'
	
	@printf 'VOLUMES:\n'
	@$(COMPOSE) volumes
	@printf '\n'
	
	@printf 'NETWORKS:\n'
	@docker network ls
	@printf '\n'

	@printf 'IMAGES:\n'
	@$(COMPOSE) images
	@printf '\n'

logs:
	$(COMPOSE) logs

# Default target of Makefile is help
help:
	@printf "%b\n" $(HELP_TEXT)

%:
	@echo "Unknown command: '$@'\n"
	@printf "%b\n" $(HELP_TEXT)

define HELP_TEXT =
	"Available commands:" \
	" make prod → Build and start in production mode" \
	" make dev → Build and start in development mode" \
	" make down → Stop and remove containers" \
	" make clean → Remove containers + images" \
	" make fclean → Full cleanup volumes" \
	" make show → Full Docker state" \
	" make logs → Show logs" \
	" make re → Clean all then run in dev mode"
endef

.PHONY: all help build up prod dev down start stop show logs ps clean fclean re %
