from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.services.users import authenticate_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/token/")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
):
    user = await authenticate_user(db, token, token)  # your simple auth
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication",
        )
    return user


async def inject_user(request: Request, user=Depends(get_current_user)):
    request.state.user = user
