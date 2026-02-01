from sqlmodel import SQLModel, Field
from typing import Optional, List
from pgvector.sqlalchemy import Vector

class Greeting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message: str

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    source: str = Field(default="unknown")
    embedding: List[float] = Field(sa_type=Vector(384)) # 384 dims for all-MiniLM-L6-v2

class Job(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    url: str
    status: str = Field(default="PENDING")
    created_at: str
    finished_at: Optional[str] = None
    result: Optional[str] = None
