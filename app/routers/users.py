# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from schemas import UserCreate, UserUpdate, TokenCreate
from services.users import create_user, authenticate_user


# ---------------------------------------------------------
# User API (ORM)
# ---------------------------------------------------------

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/create/", status_code=201)
async def user_create_route(data: UserCreate, db: AsyncSession = Depends(get_db_session)):
    try:
        user = await create_user(db, data)
        return {"id": user.id, "email": user.email, "name": user.name}
    except Exception:
        raise HTTPException(status_code=400, detail="Email already exists")


@router.get("/me/")
async def user_me_route():
    return {"email": "user@example.com", "name": "Example User"}


@router.put("/me/")
async def user_me_update_route(data: UserUpdate):
    return {"email": data.email or "user@example.com", "name": data.name or "Example User"}


@router.patch("/me/")
async def user_me_partial_update_route(data: UserUpdate):
    return {
        "email": data.email or "user@example.com",
        "name": data.name or "Example User"
    }


@router.post("/token/")
async def user_token_route(data: TokenCreate, db: AsyncSession = Depends(get_db_session)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"email": user.email, "token": "placeholder_jwt_token"}