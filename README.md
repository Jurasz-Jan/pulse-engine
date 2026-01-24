# Pulse: Self-Healing Knowledge Engine

Pulse is a local RAG (Retrieval-Augmented Generation) system designed for automated knowledge ingestion and semantic retrieval. It orchestrates asynchronous scraping, vector embedding, and LLM inference to provide a self-hosted knowledge base.

## Architecture

The system follows a microservices architecture managed via Docker Compose:

*   **Ingestion Pipeline**: 
    1.  **API Gateway**: Receives `POST /scrape` tasks.
    2.  **Task Queue (Celery + Redis)**: Asynchronously processes URLs to prevent request blocking.
    3.  **Worker**: Scrapes content, chunks text, and computes embeddings via Ollama.
    4.  **Vector Store (pgvector)**: Stores high-dimensional embeddings for semantic search.
*   **Retrieval & Inference**:
    1.  **Query**: `POST /chat` receives user input.
    2.  **Vector Search**: Computes cosine similarity against stored embeddings to retrieve relevant chunks.
    3.  **Context Construction**: Injects retrieved chunks into the LLM context window.
    4.  **Generation**: Ollama generates the final response.

## Technical Stack

*   **Core**: Python 3.11+, FastAPI (Async).
*   **Vector Database**: PostgreSQL 16 with `pgvector` extension.
*   **Task Queue**: Celery 5.3 with Redis 7 broker.
*   **Inference**: Ollama (Local LLM runtime).
*   **Orchestration**: LangChain.
*   **Frontend**: Streamlit.

## API Reference

### Endpoints

| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| `POST` | `/scrape` | Enqueue URL for ingestion | `{"url": "string"}` |
| `POST` | `/chat` | Query the knowledge base | `{"query": "string"}` |
| `GET` | `/sources` | List ingested domains | - |
| `DELETE` | `/sources` | Remove all vectors for a source | `?source=string` |
| `GET` | `/tasks/status` | Monitor Celery queue metrics | - |

## Deployment

### Prerequisites
*   Docker & Docker Compose
*   Ollama (running locally or networked) / Model pulled (e.g., `ollama pull mistral`)

### Setup

1.  **Clone & Build**:
    ```bash
    git clone <repo>
    docker-compose up --build
    ```

2.  **Services**:
    *   **Frontend**: [http://localhost:8501](http://localhost:8501)
    *   **API**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
    *   **Redis**: [localhost:6379](localhost:6379)
    *   **Postgres**: [localhost:5432](localhost:5432)

### Configuration
Environment variables are defined in `docker-compose.yml`:
*   `DATABASE_URL`: Postgres connection string.
*   `REDIS_URL`: Celery broker URL.
*   `API_URL`: Frontend-to-Backend communication channel.
