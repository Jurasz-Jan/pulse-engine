# Week 2: Asynchronous Workers - Completion Report

## Overview
This week we integrated Celery to handle background tasks, enabling the "Pulse" engine to scrape websites asynchronously. This prevents long-running operations from blocking the main API.

## Architecture Implemented
- **Celery Worker (`worker`)**: A new containerized service that listens to Redis for tasks.
- **Redis Broker**: Orchestrates message passing between FastAPI and the worker.
- **Scraping Logic**: Implemented in `app/worker.py` using `BeautifulSoup` and `requests`.

## Key Files Created/Modified
- `docker-compose.yml`: Added `worker` service.
- `requirements.txt`: Added `beautifulsoup4`, `requests`.
- `app/worker.py`: Defines the `celery_app` and `scrape_url` task.
- `app/schemas.py`: Request/Response models for scraping.
- `app/main.py`: Added `/scrape` endpoint.

## Usage

### Triggering a Scrape
```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Checking Status
Check the worker logs to see the output:
```bash
docker logs antigravity-worker-1
```

## Verification
1. `POST /scrape` returns a Task ID immediately (200 OK).
2. Worker logs show "Scraping complete for ..." shortly after.
