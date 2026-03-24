COMPOSE = docker compose
PROD_FILE = docker-compose.yml
DEV_FILE = docker-compose.override.yml

ENV = .env

all: help

# Checks if .env exists. If not it copy-creates from .env.example
$(ENV):
	@if [ ! -f "$(ENV)" ]; then \
		echo "Creating $(ENV) from .env.example"; \
		cp .env.example $(ENV); \
	fi

# Main targets/commands to build, run and and stop + clean the application
dev: $(ENV)
	@echo "Building in dev_mode"
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up --build --detach
	@echo "VOICE-CHEF is running in dev_mode"

prod: $(ENV)
	@echo "Building in prod_mode"
	$(COMPOSE) -f $(PROD_FILE) up --build --detach
	@echo "VOICE-CHEF is running in prod_mode"
	
down:
	@echo "Stopping and removing the containers..."
	$(COMPOSE) down

re: clean dev

# Clean-up targets/commands
clean:
	@echo "Stopping the app and removing containers + images..."
	$(COMPOSE) down --rmi all

fclean:
	@echo "Stopping the app and removing containers + images + volumes..."
	$(COMPOSE) down --rmi all -v --remove-orphans
	docker volume prune

# Targets/commands to show current state, logs and command
status:
	@$(COMPOSE) ps -a --format "table {{.ID}}\t{{.Name}}\t{{.Status}}\t{{.Ports}}"	
	@printf '\n'
	
	@docker volume ls --filter "label=com.docker.compose.project=$(shell basename $(PWD))"
	@printf '\n'
	
	@docker network ls --filter "label=com.docker.compose.project=$(shell basename $(PWD))"
	@printf '\n'

logs:
	$(COMPOSE) logs

# Default target of Makefile is help
help:
	@printf "%b\n" $(HELP_TEXT)

%:
	@echo "Unknown command: '$@'\n"
	@printf "%b\n" $(HELP_TEXT)

define HELP_TEXT
	"Available commands:\n" \
	" make dev:	Build and start in development mode" \
	" make prod:	Build and start in production mode" \
	" make down:	Stop and remove containers" \
	" make re:	Clean all then run in dev mode\n" \
	" make clean:	Remove containers + images" \
	" make fclean:	Remove containers + images + volumes\n" \
	" make status:	Full Docker state" \
	" make logs:	Show logs" \
	" make help:	Show available commands\n" \
	" make build:	Build images from compose file" \
	" make up:	Calling the command dev" \
	" make start:	Start the containers" \
	" make stop:	Stop running containers"
endef

# Aux targets/commands
build: $(ENV)
	$(COMPOSE) build

up: dev

start:
	$(COMPOSE) start

stop:
	$(COMPOSE) stop

.PHONY: all dev prod down re clean fclean status logs help % build up start stop
