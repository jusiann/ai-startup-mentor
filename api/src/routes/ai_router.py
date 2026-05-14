from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers import ai_controller
from src.lib.db.database import connect_db
from src.lib.db.schemas.chat_schema import ChatRequest
from src.lib.db.models.user import User
from src.lib.utils.security import get_current_user
from src.services import scraper_service

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(connect_db),
):
    return await ai_controller.chat(payload, current_user, db)


@router.get("/market-context")
async def market_context(
    topic: str = Query(..., min_length=2, max_length=200),
    current_user: User = Depends(get_current_user),
):
    data = await scraper_service.gather_market_context(topic)
    return {"success": True, "data": data}
