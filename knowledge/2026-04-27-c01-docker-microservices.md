---
id: 2026-04-27-c01
concept: Docker Compose Multi-Service Architecture
source-coverage: C01
created: 2026-04-27
---

# Docker Compose Multi-Service Architecture

Voice Chef runs as five separate Docker containers: office-frontend, kitchen-frontend, backend, agent, and db. Each is an independent microservice. Docker Compose orchestrates them — it is the blueprint to recreate the entire stack consistently on any machine.

## In Their Words
> "Microservices that are independent, like building blocks. You get a blueprint to recreate the same thing independent from the developer machine. Containers are like mini VMs that run in the docker daemon with an OS and anything the service needs."

## Connections
- [[2026-04-27-c03-backend-api]] enables — backend provides the data layer that other services depend on
- [[2026-04-27-c04-agent-service]] enables — agent is one of the containers in this architecture

## Open Questions
- Precision gap: containers share the host kernel, they don't run their own kernel (unlike VMs). Docker Desktop on macOS uses a lightweight VM to bridge this.

## Tags
#system #foundational
