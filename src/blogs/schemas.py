from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlogCreate(BaseModel):
    title: str

class BlogUpdate(BaseModel):
    title: str
    content: str

class BlogResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    status: str

    class Config:
        from_attributes = True

