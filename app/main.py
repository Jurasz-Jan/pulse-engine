from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from datetime import datetime
from app.database import init_db, get_session
from app.models import Greeting, Document, Job
from app.schemas import ScrapeRequest, TaskResponse, ChatRequest, ChatResponse, JobResponse
from app.worker import scrape_url, celery_app
from app.rag import rag_flow

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/jobs", response_model=list[JobResponse])
async def list_jobs(session: AsyncSession = Depends(get_session)):
    stmt = select(Job).order_by(Job.created_at.desc()).limit(50)
    result = await session.execute(stmt)
    return result.scalars().all()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/scrape", response_model=TaskResponse)
async def scrape(request: ScrapeRequest, session: AsyncSession = Depends(get_session)):
    # Create Job record
    job = Job(
        id=None, # will be set by celery id? No, we should probably set a UUID or let DB handle it. 
                 # Actually celery ID is good. But we want to return it.
                 # Let's generate a task first then save it.
        url=request.url,
        status="PENDING",
        created_at=datetime.utcnow().isoformat()
    )
    # Ideally we'd commit to get an ID if auto-inc, but here we can just use the task ID if we want consistency.
    # But Job.id is string (from my model edit).
    
    task = scrape_url.delay(request.url)
    
    # Use task.id as job.id
    job.id = task.id
    session.add(job)
    await session.commit()
    
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
