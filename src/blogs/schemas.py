from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlogCreate(BaseModel):
    title: str

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class BlogResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    status: str

    class Config:
        from_attributes = True

