from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class IdeaResponse(BaseModel):
    id: int
    user_id: int
    title: str
    executive_summary: Optional[str] = None
    problem_statement: Optional[str] = None
    target_audience: Optional[str] = None
    value_proposition: Optional[str] = None
    swot_analysis: Optional[dict[str, Any]] = None
    market_analysis: Optional[dict[str, Any]] = None
    business_model: Optional[str] = None
    score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IdeaListItem(BaseModel):
    id: int
    title: str
    score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
