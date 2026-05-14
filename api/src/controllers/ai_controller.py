from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.lib.db.models.user import User
from src.lib.db.models.idea import Idea
from src.lib.db.schemas.chat_schema import ChatRequest
from src.services import ai_service
from src.controllers.idea_controller import calculate_score
from src.lib.utils.error import ApiError


async def chat(payload: ChatRequest, current_user: User, db: AsyncSession):
    try:
        if not current_user:
            raise ApiError.unauthorized("User not authenticated.")

        message = payload.message.strip()
        if not message:
            raise ApiError.bad_request("Message cannot be empty.")

        result = await ai_service.process_message(
            user_id=current_user.id,
            user_message=message,
            db=db,
        )

        if result.get("idea_ready") and result.get("idea_id"):
            idea_result = await db.execute(
                select(Idea).where(Idea.id == result["idea_id"])
            )
            idea = idea_result.scalars().first()
            if idea is not None:
                idea.score = calculate_score(result)
                await db.commit()
                await db.refresh(idea)
                result["score"] = idea.score

        return JSONResponse(status_code=200, content={
            "success": True,
            "data": result,
        })
    except ApiError as error:
        return JSONResponse(
            status_code=error.status_code,
            content={"success": False, "error": error.message},
        )
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(error) or "AI processing failed"},
        )
