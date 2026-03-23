COMPOSE = docker compose
PROD_FILE = docker-compose.yml
DEV_FILE = docker-compose.override.yml

ENV = .env

all: help

$(ENV):
	@if [ ! -f "$(ENV)" ]; then \
		echo "Error: $(ENV) file not found."; \
		echo "Please copy-create it manually from .env.example."; \
		exit 1; \
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
	@echo "Stopping the containers..."
	$(COMPOSE) down

clean:
	@echo "Stopping the containers and removing the images..."
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

.PHONY: all help build up prod dev down start stop show logs clean fclean re %
