from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import init_db, get_session
from app.models import Greeting, Document
from app.schemas import ScrapeRequest, TaskResponse, ChatRequest, ChatResponse
from app.worker import scrape_url, celery_app
from app.rag import rag_flow

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/tasks/status")
async def get_task_status():
    i = celery_app.control.inspect()
    # If no workers are running, i.active() returns None
    active = i.active() or {}
    reserved = i.reserved() or {}
    
    total_active = sum(len(tasks) for tasks in active.values())
    total_queued = sum(len(tasks) for tasks in reserved.values())
    
    return {"active": total_active, "queued": total_queued}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/scrape", response_model=TaskResponse)
async def scrape(request: ScrapeRequest):
    task = scrape_url.delay(request.url)
    return {"task_id": task.id, "status": "Processing"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, session: AsyncSession = Depends(get_session)):
    result = await rag_flow(session, request.query)
    return result

@app.post("/greetings")
async def create_greeting(message: str, session: AsyncSession = Depends(get_session)):
    greeting = Greeting(message=message)
    session.add(greeting)
    await session.commit()
    await session.refresh(greeting)
    return greeting

@app.get("/greetings")
async def get_greetings(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Greeting))
    greetings = result.scalars().all()
    return greetings

@app.get("/sources")
async def list_sources(session: AsyncSession = Depends(get_session)):
    stmt = select(Document.source).distinct()
    result = await session.execute(stmt)
    return result.scalars().all()

@app.delete("/sources")
async def delete_source(source: str, session: AsyncSession = Depends(get_session)):
    from sqlalchemy import delete
    stmt = delete(Document).where(Document.source == source)
    await session.execute(stmt)
    await session.commit()
    return {"message": f"Deleted all documents from {source}"}
