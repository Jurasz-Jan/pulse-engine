# Pulse

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?logo=postgresql&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)

**Pulse** is a local-first RAG (Retrieval-Augmented Generation) engine. It manages async document ingestion, vector embeddings, and semantic search to power a self-healing knowledge base.

Built with **FastAPI**, **Celery**, **Redis**, and **pgvector**.

## ⚡ Quick Start

**Prerequisites**: [Docker Compose](https://docs.docker.com/compose/) and a running [Ollama](https://ollama.ai/) instance.

```bash
# 1. Clone
git clone <repo_url>
cd pulse

# 2. Start Services
docker-compose up --build -d

# 3. Interface
# Frontend: http://localhost:8501
# API:      http://localhost:8000/docs
```

## 🏗 Architecture

The system uses a worker-queue pattern to handle expensive scraping and embedding tasks without blocking the request loop.

```mermaid
graph LR
    Client -->|HTTP POST| API[FastAPI]
    API -->|Push Task| Redis
    Redis -->|Pop Task| Worker[Celery Worker]
    Worker -->|Scrape| Internet
    Worker -->|Embed| Ollama
    Worker -->|Write Vector| DB[(Postgres 16)]
    
    Client -->|Query| API
    API -->|Search| DB
    API -->|Context| Ollama
```

### Core Components

- **`app/worker.py`**: Background worker. Handles HTML parsing (`BeautifulSoup`), text splitting (`RecursiveCharacterTextSplitter`), and embedding generation.
- **`app/main.py`**: Async API gateway.
- **`app/rag.py`**: Retrieval logic. Performs cosine similarity search on the `document` table and builds LLM prompts.
- **Vector Store**: Postgres 16 with `pgvector`. Stores 1536d embeddings (compatible with `nomic-embed-text` or `llama2`).

## 🛠 API Usage

**1. Ingest URL**
Triggers a background job. Returns a Task ID immediately.
```bash
curl -X POST "http://localhost:8000/scrape" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://fastapi.tiangolo.com/async/"}'
```

**2. Chat with Data**
Queries the indexed knowledge base.
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "How does async/await work in Python?"}'
```

## 📦 Project Structure

```text
.
├── app/
│   ├── worker.py     # Celery tasks (Scraping/Embedding)
│   ├── rag.py        # RAG pipeline implementation
│   ├── frontend.py   # Streamlit UI
│   ├── database.py   # Async SQLAlchemy setup
│   └── models.py     # SQLModel schemas
├── docker-compose.yml
└── requirements.txt
```

## 🔧 Local Development

To run the stack manually (without Docker for the app):

1.  **Start Infrastructure**:
    ```bash
    docker-compose up db redis -d
    ```
2.  **Environment Setup**:
    ```bash
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Run Worker**:
    ```bash
    # Requires local Redis/PG connection env vars
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/pulse"
    export REDIS_URL="redis://localhost:6379/0"
    celery -A app.worker.celery_app worker --loglevel=info
    ```
4.  **Run API**:
    ```bash
    uvicorn app.main:app --reload
    ```

## Roadmap

- [ ] Rate limiting for scraper.
- [ ] Websocket support for real-time task progress.
- [ ] PDF/Text file upload support.
