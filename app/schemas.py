from pydantic import BaseModel

class ScrapeRequest(BaseModel):
    url: str

class TaskResponse(BaseModel):
    task_id: str
    status: str

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    trace: list[str]
    sources: list[str]
