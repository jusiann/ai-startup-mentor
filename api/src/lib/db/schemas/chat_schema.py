from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    session_id: Optional[str] = None
    message: str

class MessageResponse(BaseModel):
    id: int
    sender: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True
