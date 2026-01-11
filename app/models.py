from sqlmodel import SQLModel, Field
from typing import Optional, List
from pgvector.sqlalchemy import Vector

class Greeting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message: str

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    embedding: List[float] = Field(sa_type=Vector(384)) # 384 dims for all-MiniLM-L6-v2
