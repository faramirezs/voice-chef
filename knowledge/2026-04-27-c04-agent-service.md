---
id: 2026-04-27-c04
concept: Agent Service (Pydantic AI)
source-coverage: C04
created: 2026-04-27
---

# Agent Service (Pydantic AI)

The agent is a Python service using Pydantic AI. It does NOT talk to the database directly. Instead, it has tool functions (Python) that use httpx to call the backend REST API endpoints. The chain is: agent tool -> HTTP call -> backend API -> SQLAlchemy -> PostgreSQL. The agent is responsible for understanding user intentions and making the frontend more accessible.

## In Their Words
> "The agent helps the user access data and makes the frontend more accessible by understanding intentions. The agent has tools, and some of the tools are python functions that fetch the endpoints from the database."

## Connections
- [[2026-04-27-c03-backend-api]] applies-in — agent calls backend API via httpx, never touches DB directly
- [[2026-04-27-c01-docker-microservices]] is-a — agent is one of the Docker containers

## Open Questions
(none)

## Tags
#system #intermediate
