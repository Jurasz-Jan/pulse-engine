from sqlmodel import SQLModel, Field
from typing import Optional

class Greeting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message: str
