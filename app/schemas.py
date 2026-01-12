from pydantic import BaseModel

class ScrapeRequest(BaseModel):
    url: str

class TaskResponse(BaseModel):
    task_id: str
    status: str

class JobResponse(BaseModel):
    id: str
    url: str
    status: str
    created_at: str
    finished_at: str | None
    result: str | None

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    trace: list[str]
    sources: list[str]
