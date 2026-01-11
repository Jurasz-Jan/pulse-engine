from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import init_db, get_session
from app.models import Greeting
from app.schemas import ScrapeRequest, TaskResponse
from app.worker import scrape_url

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/scrape", response_model=TaskResponse)
async def scrape(request: ScrapeRequest):
    task = scrape_url.delay(request.url)
    return {"task_id": task.id, "status": "Processing"}

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
