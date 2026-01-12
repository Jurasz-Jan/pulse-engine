# Week 4: The "Self-Correction" Loop & UI - Completion Report

## Overview
We added "brain" to the system. It now critiques its own work and fixes it. We also added a Face (Streamlit UI).

## Architecture Changes
- **Agentic Loop**: `/chat` now orchestrates `Grade -> Rewrite -> Search` loops.
- **Frontend**: A generic Streamlit container talking to the API.

## How to Run
Ensure the full stack is running:
```bash
docker compose up --build -d
```

## Access the UI
Navigate to **[http://localhost:8501](http://localhost:8501)**.

1.  **Ingest Tab**: Enter `https://fastapi.tiangolo.com` or `https://www.python.org`.
2.  **Chat Tab**: Ask "What is this?" or "Tell me about it".  
    *Watch the "Thought Process" expendable to see it think!*

## Manage Knowledge Base (Sources)
You can manage the ingested documents using the API:

### List Sources
See what websites are currently stored in the database:
```bash
curl http://localhost:8000/sources
```

### Delete a Source
Remove all documents associated with a specific URL:
```bash
curl -X DELETE "http://localhost:8000/sources?source=https://www.python.org/"
```

## Verification
```bash
python tests/verify.py
```

## Note on Performance
Running 3 LLM calls (Draft, Grade, Rewrite) + Embeddings locally is **heavy**. Expect 30-60s latency per message on standard hardware without a GPU.
