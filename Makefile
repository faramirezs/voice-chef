# ═══════════════════════════════════════════════════════════════════════════
# Voice Chef — Makefile
# ═══════════════════════════════════════════════════════════════════════════
#
# Quick start:
#   make dev          → Full dev stack (all services, hot-reload)
#   make prod         → Production deployment (nginx reverse proxy + SSL)
#
# IMPORTANT:
#   All build targets use --no-cache to avoid stale Docker layer bugs
#   when switching between dev (target: dev) and prod (target: runtime).
#   See: https://github.com/moby/moby/issues/38379
#
# ═══════════════════════════════════════════════════════════════════════════

COMPOSE = docker compose
PROD_FILE = docker-compose.yml
DEV_FILE = docker-compose.override.yml
ENV = .env

# ── Default target ─────────────────────────────────────────────────────────
all: help

# ── Environment bootstrap ──────────────────────────────────────────────────
# Copy-creates .env from .env.example if it does not exist.
$(ENV):
	@test -f $(ENV) || (cp .env.example $(ENV) && echo "Created $(ENV) from .env.example")

# ── Development targets ────────────────────────────────────────────────────

# Use these when working locally. They mount source code as volumes for
# hot-reload and bind service ports directly to the host.
#
#   make dev              Start everything (fast: reuses Docker layer cache)
#   make dev-re           Same as dev but builds from scratch (--no-cache).
#                         Use this if switching from prod or seeing stale
#                         layer issues (e.g. wrong target: dev vs runtime).
#   make dev-back         Start only db + backend (for API-only work)
#   make dev-back-office  Start db + backend + office-frontend
#   make up               Start existing containers (no rebuild, fastest)

# Dev mode access:
# - Office: http://localhost:5173
# - Kitchen: http://localhost:5174
# - Backend API: http://localhost:8000

dev: $(ENV)
	@echo "Building and starting in dev_mode (cached)"
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up --build
	@echo "VOICE-CHEF is running in dev_mode"

dev-re: $(ENV)
	@echo "Building fresh images and starting in dev_mode"
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) build --no-cache
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up
	@echo "VOICE-CHEF is running in dev_mode"

dev-back: $(ENV)
	@echo "Building and running db and backend services in dev_mode"
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up -d --build db backend

dev-back-office: $(ENV)
	@echo "Building and running db, backend and office-frontend services in dev_mode"
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up -d --build db backend office-frontend

up: $(ENV)
	@echo "Starting in dev_mode"
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) up
	@echo "VOICE-CHEF is running in dev_mode"

# ── Production target ──────────────────────────────────────────────────────

# Use this for VPS / CI-CD deployments. Builds all images from scratch
# (--no-cache) then recreates containers with zero-downtime rolling.
#
#   make prod   Build fresh images and restart all services
#
# The shared nginx-proxy terminates SSL on 443 and routes:
#   /            → office-frontend
#   /kitchen/    → kitchen-frontend
#   /api/        → backend
#   /agent/      → agent (WebSocket-capable)
#   /stt/        → stt
#   /uploads/    → backend
#   /docs        → backend (Swagger)
#   /openapi.json → backend

prod: $(ENV)
	@echo "Stopping existing containers, building fresh images and restarting in prod_mode"
	$(COMPOSE) -f $(PROD_FILE) down
	$(COMPOSE) -f $(PROD_FILE) build --no-cache
	$(COMPOSE) -f $(PROD_FILE) up --remove-orphans
	@echo "VOICE-CHEF is running in prod_mode"

# ── Lifecycle targets ──────────────────────────────────────────────────────
#   make down   Stop and remove containers (images + volumes are kept)
#   make start  Start stopped containers (no rebuild)
#   make stop   Stop running containers (no removal)

down:
	@echo "Stopping and removing the containers..."
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) down
	@echo "Done."

start:
	@echo "Starting the containers..."
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) start

stop:
	@echo "Stopping the containers..."
	$(COMPOSE) -f $(PROD_FILE) -f $(DEV_FILE) stop

# ── Clean-up targets ───────────────────────────────────────────────────────
#   make clean       Remove containers + images (keeps volumes & data)
#   make clean-nginx Remove ALL images including nginx (keeps database volume)
#   make fclean      NUCLEAR OPTION: removes everything including volumes
#                    (WARNING: this wipes the database and uploaded files)

clean:
	@echo "Stopping the app and removing containers + images..."
	$(COMPOSE) down --rmi local --remove-orphans

clean-nginx: clean
	@echo "Removing ALL Docker images (including nginx-proxy)..."
	$(COMPOSE) stop nginx-proxy  || true	
	$(COMPOSE) rm -f nginx-proxy
	docker rmi voice-chef-nginx-proxy:latest
	@echo "All images removed. Database volume preserved."

fclean:
	@echo "Stopping the app and removing containers + images + volumes..."
	$(COMPOSE) down --rmi all -v --remove-orphans
	docker volume prune -f
	@echo "Nuclear cleanup complete. Database and uploads are gone."

# ── Full reset + dev start ─────────────────────────────────────────────────

re: clean dev

# ── Observability targets ──────────────────────────────────────────────────
#   make status   Show running containers, ports, images, volumes
#   make logs     Stream logs from all services

status:
	@$(COMPOSE) ps -a --format "table {{.ID}}\t{{.Name}}\t{{.Status}}\t{{.Ports}}"
	@printf '\n'
	@docker volume ls --filter "label=com.docker.compose.project=$(shell basename $(PWD))"
	@printf '\n'
	@docker network ls --filter "label=com.docker.compose.project=$(shell basename $(PWD))"
	@printf '\n'
	@( \
		printf "IMAGE\tID\tSIZE\n"; \
		docker images \
			--filter "label=com.docker.compose.project=$(shell basename $(PWD))" \
			--format "{{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}"; \
		docker images postgres \
			--format "{{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}"; \
	) | column -t; \
		printf '\n'

logs:
	@docker compose logs

# ── Build target (no start) ────────────────────────────────────────────────
#   make build   Build all images without starting containers.
#                Useful for CI caching or verifying Dockerfile changes.

build: $(ENV)
	@echo "Building images..."
	$(COMPOSE) build --no-cache

# ── Per-service targets (for targeted rebuilds / debugging) ────────────────

agent-build: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) build agent

agent-build-nocache: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) build --no-cache agent

agent-recreate: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) up -d --build --force-recreate agent

stt-build: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) build stt

stt-build-nocache: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) build --no-cache stt

stt-recreate: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) up -d --build --force-recreate stt

refresh-env-agent: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) up -d --build --force-recreate backend agent

# ── Database targets ───────────────────────────────────────────────────────

LOCAL_DB_URL = $$( \
    USER=$$(grep POSTGRES_USER .env | cut -d= -f2); \
    PASS=$$(grep POSTGRES_PASSWORD .env | cut -d= -f2); \
    NAME=$$(grep POSTGRES_DB .env | cut -d= -f2); \
    echo "postgresql+psycopg://$$USER:$$PASS@localhost:5432/$$NAME" \
)

# Run all four schema-drift gates locally (strict check).
drift-gate-local: $(ENV)
	@echo "Running local 4-gate schema drift check..."
	@chmod +x db/scripts/run_local_drift_gate.sh
	@DATABASE_URL=$(LOCAL_DB_URL) ./db/scripts/run_local_drift_gate.sh
	@echo "Done: local schema drift gate passed"

# Blast-test: wipe DB volume, re-initialize from dump, then run alembic upgrade.
dump-blast-check:
	@chmod +x db/scripts/dump_upgrade_blast_check.sh
	@DATABASE_URL=$(LOCAL_DB_URL) ./db/scripts/dump_upgrade_blast_check.sh

# Regenerate db/init/01_dump.sql from the current migration head.
dump-regen:
	@echo "Regenerating db/init/01_dump.sql from migration head (isolated temp DB)..."
	chmod +x db/scripts/regenerate_dump_from_head.sh
	./db/scripts/regenerate_dump_from_head.sh
	@echo "Done: db/init/01_dump.sql regenerated from migration head"

# Open a psql shell inside the running db container.
db-connect:
	@docker compose exec db psql -U $(shell grep POSTGRES_USER .env | cut -d= -f2) -d $(shell grep POSTGRES_DB .env | cut -d= -f2)

# Open a bash shell inside the running agent container.
agent-terminal:
	@docker compose exec agent bash

# ═══════════════════════════════════════════════════════════════════════════
# Help
# ═══════════════════════════════════════════════════════════════════════════

help:
	@printf "\n"
	@printf "╔════════════════════════════════════════════════════════════════════════════╗\n"
	@printf "║                      Voice Chef — Available Commands                       ║\n"
	@printf "╚════════════════════════════════════════════════════════════════════════════╝\n"
	@printf "\n  🚀  START (pick one)\n"
	@printf "     %-30s %s\n" "make dev"         "Full dev stack (cached build, fast)"
	@printf "     %-30s %s\n" "make dev-re"      "Full dev stack (clean build, --no-cache)"
	@printf "     %-30s %s\n" "make prod"        "Production mode (nginx SSL proxy, no direct host ports)"
	@printf "     %-30s %s\n" "make up"          "Restart existing dev containers (no rebuild)"
	@printf "\n  🧩  PARTIAL DEV (lightweight)\n"
	@printf "     %-30s %s\n" "make dev-back"          "Only db + backend"
	@printf "     %-30s %s\n" "make dev-back-office"   "Only db + backend + office-frontend"
	@printf "\n  🛑  STOP / CLEAN\n"
	@printf "     %-30s %s\n" "make down"        "Stop and remove containers"
	@printf "     %-30s %s\n" "make stop"        "Stop containers (keep them)"
	@printf "     %-30s %s\n" "make clean"       "Remove containers + images (keeps data)"
	@printf "     %-30s %s\n" "make clean-nginx" "Remove ALL images including nginx (keeps DB)"
	@printf "     %-30s %s\n" "make fclean"      "⚠️  NUCLEAR: removes everything including DB + uploads"
	@printf "\n  🔧  PER-SERVICE REBUILDS\n"
	@printf "     %-30s %s\n" "make agent-build-nocache"  "Rebuild agent from scratch"
	@printf "     %-30s %s\n" "make stt-build-nocache"    "Rebuild STT from scratch"
	@printf "     %-30s %s\n" "make refresh-env-agent"    "Recreate backend + agent with fresh env"
	@printf "\n  👁  OBSERVE\n"
	@printf "     %-30s %s\n" "make status"      "Containers, images, and volumes"
	@printf "     %-30s %s\n" "make logs"        "Stream all service logs"
	@printf "\n  🗄  DATABASE\n"
	@printf "     %-30s %s\n" "make db-connect"          "Open psql shell in db container"
	@printf "     %-30s %s\n" "make drift-gate-local"    "Run local schema-drift checks"
	@printf "     %-30s %s\n" "make dump-blast-check"    "Test dump-init → alembic upgrade"
	@printf "     %-30s %s\n" "make dump-regen"          "Regenerate db/init/01_dump.sql"
	@printf "\n"

# ── Fallback ───────────────────────────────────────────────────────────────
# Catch-all for unrecognized targets.
%:
	@echo "Unknown target '$@'. Run 'make help' for available commands."
.PHONY: all dev dev-re dev-back dev-back-office prod down re clean clean-nginx fclean status logs help build up start stop
.PHONY: agent-build agent-build-nocache agent-recreate stt-build stt-build-nocache stt-recreate
.PHONY: refresh-env-agent dump-blast-check dump-regen drift-gate-local db-connect agent-terminal
