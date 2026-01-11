from pydantic import BaseModel

class ScrapeRequest(BaseModel):
    url: str

class TaskResponse(BaseModel):
    task_id: str
    status: str
