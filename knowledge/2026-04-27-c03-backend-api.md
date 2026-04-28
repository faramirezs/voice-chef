---
id: 2026-04-27-c03
concept: Backend REST API (FastAPI)
source-coverage: C03
created: 2026-04-27
---

# Backend REST API (FastAPI)

The backend is a FastAPI (Python) service that serves data. It communicates with the PostgreSQL database using SQLAlchemy/SQLModel. Other services (kitchen frontend, agent) talk to it via REST endpoints under /api. It is the single source of truth for data access.

## In Their Words
> "The backend is responsible for serving data, and for keeping communication with the db."

## Connections
- [[2026-04-27-c01-docker-microservices]] is-a — backend is one of the Docker containers
- [[2026-04-27-c04-agent-service]] enables — agent calls backend API to get data (agent has no direct DB access)

## Open Questions
(none)

## Tags
#system #foundational
