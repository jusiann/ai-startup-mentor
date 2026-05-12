from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from src.lib.db.models.chat import ChatHistory
from src.lib.db.models.idea import Idea
from src.lib.db.schemas import chat_schema
from src.lib.db.models.user import User
from src.lib.utils.error import ApiError
from src.services.ai_service import AIService

async def send_message(payload: chat_schema.MessageCreate, current_user: User, db: AsyncSession):
    try:
        # Generate session_id if none provided
        session_id = payload.session_id or str(uuid.uuid4())

        # Check if session is already converted into an idea
        result = await db.execute(
            select(Idea).where(Idea.session_id == session_id, Idea.user_id == current_user.id)
        )
        if result.scalars().first():
            raise ApiError.bad_request("This chat session has expired because the idea was already generated.")

        # Save user message
        user_msg = ChatHistory(
            user_id=current_user.id,
            session_id=session_id,
            sender="user",
            message=payload.message
        )
        db.add(user_msg)
        await db.flush()

        # Process with AI
        ai_result = await AIService.process_message(session_id, payload.message, current_user.id, db)
        
        # Save AI reply
        ai_msg = ChatHistory(
            user_id=current_user.id,
            session_id=session_id,
            sender="ai",
            message=ai_result["reply"]
        )
        db.add(ai_msg)
        await db.commit()

        return JSONResponse(status_code=200, content={
            "status": "success",
            "session_id": session_id,
            "reply": ai_result["reply"],
            "idea_created": ai_result["idea_created"],
            "created_idea_id": ai_result["created_idea_id"]
        })
    except ApiError as error:
        await db.rollback()
        return JSONResponse(status_code=error.status_code, content={"success": False, "error": error.message})
    except Exception as error:
        await db.rollback()
        return JSONResponse(status_code=500, content={"success": False, "error": str(error) or "Failed to process message"})

async def get_messages(session_id: str, current_user: User, db: AsyncSession):
    try:
        result = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.session_id == session_id, ChatHistory.user_id == current_user.id)
            .order_by(ChatHistory.created_at)
        )
        messages = result.scalars().all()
        
        data = [{
            "id": msg.id,
            "sender": msg.sender,
            "message": msg.message,
            "timestamp": msg.created_at.isoformat()
        } for msg in messages]

        return JSONResponse(status_code=200, content=data)
    except Exception as error:
        return JSONResponse(status_code=500, content={"success": False, "error": str(error) or "Failed to retrieve messages"})
