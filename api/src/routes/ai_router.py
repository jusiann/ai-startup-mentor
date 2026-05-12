from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.lib.db.database import get_db
from src.lib.db.schemas import chat_schema
from src.lib.db.models.user import User
from src.lib.utils.security import get_current_user # Assuming this exists based on auth
from src.controllers import ai_controller

router = APIRouter(prefix="/api/ai", tags=["AI"])

@router.post("/send-message")
async def send_message_route(
    payload: chat_schema.MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ai_controller.send_message(payload, current_user, db)

@router.get("/messages/{session_id}")
async def get_messages_route(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ai_controller.get_messages(session_id, current_user, db)
