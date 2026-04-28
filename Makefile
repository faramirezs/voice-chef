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
	@echo "Building and starting in dev_mode"
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up --build
	@echo "VOICE-CHEF is running in dev_mode"

up: $(ENV)
	@echo "Starting in dev_mode"
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up
	@echo "VOICE-CHEF is running in dev_mode"

dev-back: $(ENV)
	@echo "Building and running db and backend services in dev_mode"
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up -d --build db backend

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
	" make dev-back:	Build and run db and backend in dev mode" \
	" make prod:	Build and start in production mode" \
	" make down:	Stop and remove containers" \
	" make re:	Clean all then run in dev mode\n" \
	" make clean:	Remove containers + images" \
	" make fclean:	Remove containers + images + volumes\n" \
	" make status:	Full Docker state" \
	" make logs:	Show logs" \
	" make drift-gate-local:	Run local 4-gate schema drift check (strict pending-autogen gate)" \
	" make dump-blast-check:	Reset DB volume and test dump-init -> alembic head upgrade" \
	" make dump-regen:	Regenerate db/init/01_dump.sql from migration head" \
	" make help:	Show available commands\n" \
	" make build:	Build images from compose file" \
	" make agent-build:\tBuild only agent service" \
	" make agent-build-nocache:\tBuild only agent service without cache" \
	" make agent-recreate:\tRecreate and run only agent service\n" \
	" make stt-build:\tBuild only stt service" \
	" make stt-build-nocache:\tBuild only stt service without cache" \
	" make stt-recreate:\tRecreate and run only stt service\n" \
	" make refresh-env-agent:\tRecreate backend and agent with fresh env\n" \
	" make up:	Calling the command dev" \
	" make start:	Start the containers" \
	" make stop:	Stop running containers"
endef

# Aux targets/commands
build: $(ENV)
	$(COMPOSE) build

agent-build: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) build agent

agent-build-nocache: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) build --no-cache agent

agent-recreate: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up -d --force-recreate agent

stt-build: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) build stt

stt-build-nocache: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) build --no-cache stt

stt-recreate: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up -d --force-recreate stt

refresh-env-agent: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up -d --no-deps --force-recreate backend agent

start:
	$(COMPOSE) start

stop:
	$(COMPOSE) stop

dump-blast-check:
	chmod +x db/scripts/dump_upgrade_blast_check.sh
	./db/scripts/dump_upgrade_blast_check.sh

dump-regen:
	@echo "Regenerating db/init/01_dump.sql from migration head (isolated temp DB)..."
	chmod +x db/scripts/regenerate_dump_from_head.sh
	./db/scripts/regenerate_dump_from_head.sh
	@echo "Done: db/init/01_dump.sql regenerated from migration head"

drift-gate-local:
	@echo "Running local 4-gate schema drift check..."
	chmod +x db/scripts/run_local_drift_gate.sh
	./db/scripts/run_local_drift_gate.sh
	@echo "Done: local schema drift gate passed"

db-connect:
	docker exec -it voice-chef-db-1 psql -h localhost -p 5432 -U recipe_user -d recipe_db

agent-terminal:
	docker exec -it voice-chef-agent-1 bash

.PHONY: all dev dev-back prod down re clean fclean status logs help % build up start stop
.PHONY: agent-build agent-build-nocache agent-recreate stt-build stt-build-nocache stt-recreate
.PHONY: refresh-env-agent dump-blast-check dump-regen drift-gate-local db-connect agent-terminal 
