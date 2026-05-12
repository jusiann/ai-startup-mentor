from pydantic import BaseModel
from datetime import datetime

class IdeaResponse(BaseModel):
    id: int
    title: str
    executive_summary: str
    market_analysis: str
    swot_analysis: str
    business_model: str
    created_at: datetime

    class Config:
        from_attributes = True

class IdeaSummaryResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True
