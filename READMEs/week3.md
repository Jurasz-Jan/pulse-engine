# Week 3: Vector Database & RAG (Local) - Completion Report

## Overview
We successfully implemented a fully local Retrieval-Augmented Generation (RAG) system. This updated the architecture to use `pgvector` for storage and local models (`all-MiniLM-L6-v2` and `llama3`) for intelligence.

## Architecture Implemented
- **Vector DB**: `pgvector` extension enabled in PostgreSQL.
- **Embeddings**: `SentenceTransformers` running on CPU in the `worker`.
- **Inference**: `Ollama` running `llama3` in a dedicated container.
- **RAG Pipeline**:
    - **Ingestion**: Scrape -> Chunk -> Embed -> Store.
    - **Retrieval**: Query -> Embed -> Vector Search (L2 Distance).
    - **Generation**: Context + Query -> Llama 3 -> Answer.

## Quick Start (Build from Scratch)

### 1. Start the Stack
Run the following to build and start all services (FastAPI, Redis, Postgres/pgvector, Ollama):
```bash
docker compose up --build -d
```

### 2. Prepare Local Models
Once the containers are running (check with `docker ps`), verify Ollama is ready and pull the Llama 3 model:
```bash
docker exec antigravity-ollama-1 ollama pull llama3
```
*Note: This downloads ~4.7GB and may take a few minutes.*

## Verification / Sanity Check

We have provided an automated script to verify the deployment health, scraping capability, and validation logic.

### 1. Install Test Dependencies (Local)
```bash
pip install httpx
```

### 2. Run the Sanity Check
```bash
python tests/verify.py
```
*Expected Output:*
```text
Running automated tests against http://localhost:8000
Testing / ... OK
Testing POST /scrape ... OK (Task ID: ...)
Testing POST /chat validation ... OK (Correctly rejected)
All tests passed! ✅
```

## Manual Usage
### Ingest Data
```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.python.org/"}'
```

### Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?"}'
```

## Troubleshooting
- **Build Failures**: Ensure `build-essential` is in the Dockerfile if using `python:slim` images.
- **Timeouts**: Local inference can be slow. Increase timeout clients if needed.
