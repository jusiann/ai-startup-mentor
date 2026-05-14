from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers import idea_controller
from src.lib.db.database import connect_db
from src.lib.db.models.user import User
from src.lib.utils.security import get_current_user

router = APIRouter(prefix="/api/ideas", tags=["Ideas"])


@router.get("/")
async def list_ideas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(connect_db),
):
    return await idea_controller.list_ideas(current_user, db)


@router.get("/{idea_id}")
async def get_idea(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(connect_db),
):
    return await idea_controller.get_idea(idea_id, current_user, db)


@router.delete("/{idea_id}")
async def delete_idea(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(connect_db),
):
    return await idea_controller.delete_idea(idea_id, current_user, db)


@router.get("/{idea_id}/export.csv")
async def export_csv(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(connect_db),
):
    return await idea_controller.export_csv(idea_id, current_user, db)


@router.get("/{idea_id}/export.pdf")
async def export_pdf(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(connect_db),
):
    return await idea_controller.export_pdf(idea_id, current_user, db)
