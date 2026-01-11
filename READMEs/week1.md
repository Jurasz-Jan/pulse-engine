# Week 1: Skeleton & Docker - Completion Report

## Overview
This week focused on establishing the core infrastructure for the "Pulse" project. We successfully containerized the application and set up the necessary services for the upcoming asynchronous and vector database features.

## Architecture Implemented
- **FastAPI Service (`web`)**: The core application server running Python 3.12.
- **PostgreSQL Database (`db`)**: Primary data store, running PostgreSQL 15. Configured with the `pgvector` environment (ready for vector search).
- **Redis (`redis`)**: Message broker, running Redis 7. Will be used by Celery in Week 2.
- **Docker Compose**: Orchestrates all three services for a consistent development environment.

## Key Files Created
- `docker-compose.yml`: Service definitions.
- `Dockerfile`: Build instructions for the FastAPI app.
- `app/main.py`: Application entry point with "Hello World" and DB checks.
- `app/database.py`: Async database connection using SQLModel and AsyncPG.
- `app/models.py`: Initial data models.
- `app/settings.py`: Configuration management.

## Usage

### Prerequisites
- Docker & Docker Compose

### Running the Project
To start the entire stack:
```bash
docker compose up --build -d
```
The API will be available at http://localhost:8000.

### Stopping
```bash
docker compose down
```

## Verification
The system was verified by:
1. Spinning up all containers using `docker compose up --build -d`.
2. Accessing the root endpoint: `GET /` -> `{"message": "Hello World"}`.
3. Writing to the database: `POST /greetings` -> Successfully saved and returned a greeting.
