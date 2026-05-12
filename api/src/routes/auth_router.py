from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from src.controllers import auth_controller
from src.lib.db.database import get_db
from src.lib.db.schemas import user_schema
from src.lib.db.models.user import User
from src.lib.utils.security import get_current_user

router = APIRouter()

@router.post("/register")
async def register(user_data: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
    return await auth_controller.register(user_data, db)

@router.post("/login")
async def login(
    user_data: Optional[user_schema.UserLogin] = Body(None), 
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    # Eğer JSON gelmediyse (Swagger Formu kullanılıyorsa) veriyi Form'dan al
    if user_data is None:
        user_data = user_schema.UserLogin(email=form_data.username, password=form_data.password)
    
    return await auth_controller.login(user_data, db)

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return await auth_controller.logout(current_user)

@router.delete("/delete-account")
async def delete_account(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await auth_controller.delete_account(current_user, db)
