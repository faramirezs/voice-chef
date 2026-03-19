COMPOSE = docker compose
PROD_FILE = docker-compose.yml
DEV_FILE = docker-compose.override.yml

ENV = .env

all: up

$(ENV): .env.example
	cp .env.example $(ENV)

build: $(ENV)
	$(COMPOSE) build

up: $(ENV)
	$(COMPOSE) up --build --detach

prod: $(ENV)
	$(COMPOSE) -f $(PROD_FILE) up --build --detach

down:
	$(COMPOSE) down

start:
	$(COMPOSE) start

stop:
	$(COMPOSE) stop

show:
	@docker compose ps -a
	@echo "\n"
	@docker volume ls
	@echo "\n"
	@docker network ls
# 	@docker images
# 	@echo "\n"

logs:
	$(COMPOSE) logs

ps:
	$(COMPOSE) ps -a

clean:
	$(COMPOSE) down --rmi all

re: clean all

fclean: clean
	$(COMPOSE) down --rmi all -v --remove-orphans
	rm -f .env

.PHONY: all build up down re stop start show logs ps clean fclean