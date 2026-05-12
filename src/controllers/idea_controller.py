from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.lib.db.models.idea import Idea
from src.lib.db.models.user import User
from src.lib.utils.error import ApiError

async def get_ideas(current_user: User, db: AsyncSession):
    try:
        result = await db.execute(select(Idea).where(Idea.user_id == current_user.id))
        ideas = result.scalars().all()
        
        data = [{
            "id": idea.id,
            "title": idea.title,
            "created_at": idea.created_at.isoformat()
        } for idea in ideas]
        
        return JSONResponse(status_code=200, content=data)
    except Exception as error:
        return JSONResponse(status_code=500, content={"success": False, "error": str(error) or "Failed to retrieve ideas"})

async def get_idea_details(idea_id: int, current_user: User, db: AsyncSession):
    try:
        result = await db.execute(select(Idea).where(Idea.id == idea_id, Idea.user_id == current_user.id))
        idea = result.scalars().first()
        
        if not idea:
            raise ApiError.not_found("Idea not found or unauthorized.")
            
        return JSONResponse(status_code=200, content={
            "id": idea.id,
            "title": idea.title,
            "executive_summary": idea.executive_summary,
            "market_analysis": idea.market_analysis,
            "swot_analysis": idea.swot_analysis,
            "business_model": idea.business_model,
            "created_at": idea.created_at.isoformat()
        })
    except ApiError as error:
        return JSONResponse(status_code=error.status_code, content={"success": False, "error": error.message})
    except Exception as error:
        return JSONResponse(status_code=500, content={"success": False, "error": str(error) or "Failed to retrieve idea details"})

async def delete_idea(idea_id: int, current_user: User, db: AsyncSession):
    try:
        result = await db.execute(select(Idea).where(Idea.id == idea_id, Idea.user_id == current_user.id))
        idea = result.scalars().first()
        
        if not idea:
            raise ApiError.not_found("Idea not found or unauthorized.")
            
        await db.delete(idea)
        await db.commit()
        
        # 204 No Content
        from fastapi import Response
        return Response(status_code=204)
    except ApiError as error:
        return JSONResponse(status_code=error.status_code, content={"success": False, "error": error.message})
    except Exception as error:
        return JSONResponse(status_code=500, content={"success": False, "error": str(error) or "Failed to delete idea"})
