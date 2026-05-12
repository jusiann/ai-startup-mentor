from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.lib.db.database import get_db
from src.lib.db.models.user import User
from src.lib.utils.security import get_current_user
from src.controllers import idea_controller

router = APIRouter(prefix="/api/ideas", tags=["Ideas"])

@router.get("/")
async def get_ideas_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await idea_controller.get_ideas(current_user, db)

@router.get("/{idea_id}")
async def get_idea_details_route(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await idea_controller.get_idea_details(idea_id, current_user, db)

@router.delete("/{idea_id}")
async def delete_idea_route(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await idea_controller.delete_idea(idea_id, current_user, db)
