from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta

from src.lib.db.models.user import User
from src.lib.db.schemas import user_schema
from src.lib.utils.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from src.lib.utils.error import ApiError

async def register(user_data: user_schema.UserCreate, db: AsyncSession):
    try:
        if len(user_data.fullname) < 2 or len(user_data.fullname) > 50:
            raise ApiError.bad_request("Full name must be between 2 and 50 characters long.")

        if len(user_data.password) < 8 or len(user_data.password) > 72:
            raise ApiError.bad_request("Password must be between 8 and 72 characters long.")

        result = await db.execute(select(User).where(User.email == user_data.email.lower()))
        existing_user = result.scalars().first()
        
        if existing_user:
            raise ApiError.conflict("Email already exists.")
        
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            fullname=user_data.fullname.strip(),
            email=user_data.email.lower(),
            password_hash=hashed_password,
            country=user_data.country,
            city=user_data.city
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.email}, expires_delta=access_token_expires
        )
        
        return JSONResponse(status_code=201, content={
            "success": True,
            "message": "Sign-up Successful",
            "access_token": access_token,
            "user": {
                "id": new_user.id,
                "fullname": new_user.fullname,
                "email": new_user.email,
                "country": new_user.country,
                "city": new_user.city
            }
        })
    except ApiError as error:
        return JSONResponse(status_code=error.status_code, content={"success": False, "error": error.message})
    except Exception as error:
        return JSONResponse(status_code=500, content={"success": False, "error": str(error) or "Sign-up Failed"})

async def login(user_data: user_schema.UserLogin, db: AsyncSession):
    try:
        result = await db.execute(select(User).where(User.email == user_data.email.lower()))
        user = result.scalars().first()
        
        is_password_valid = False
        if user:
            is_password_valid = verify_password(user_data.password, user.password_hash)
            
        if not user or not is_password_valid:
            raise ApiError.unauthorized("Invalid email or password.")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Sign-in successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "fullname": user.fullname,
                "email": user.email,
                "country": user.country,
                "city": user.city
            }
        })
    except ApiError as error:
        return JSONResponse(status_code=error.status_code, content={"success": False, "error": error.message})
    except Exception as error:
        return JSONResponse(status_code=500, content={"success": False, "error": str(error) or "Sign-in Failed"})

async def logout(current_user: User):
    try:
        if not current_user:
            raise ApiError.not_found("User not found.")
            
        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Logged out successfully."
        })
    except ApiError as error:
        return JSONResponse(status_code=error.status_code, content={"success": False, "error": error.message})
    except Exception as error:
        return JSONResponse(status_code=500, content={"success": False, "error": str(error) or "Logout failed"})

async def delete_account(current_user: User, db: AsyncSession):
    try:
        if not current_user:
            raise ApiError.not_found("User not found.")
            
        await db.delete(current_user)
        await db.commit()
        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Account deleted successfully."
        })
    except ApiError as error:
        return JSONResponse(status_code=error.status_code, content={"success": False, "error": error.message})
    except Exception as error:
        return JSONResponse(status_code=500, content={"success": False, "error": str(error) or "Account deletion failed"})
