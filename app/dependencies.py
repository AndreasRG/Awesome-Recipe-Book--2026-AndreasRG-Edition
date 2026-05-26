from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import User

# Use OAuth2 password bearer only for optional token extraction.
# auto_error=False allows requests to proceed if no bearer token is present.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/token/", auto_error=False)


async def get_current_user(
    request: Request = None,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
):
    """Get current user from cookie or token. Raises HTTPException if not found."""
    user_id = None

    # Try to get authenticated user from cookie first.
    # This is the primary session mechanism for browser-based login.
    if request:
        user_id = request.cookies.get("user_id")

    # If no cookie exists, fall back to token-based auth.
    # In this app token is currently treated as a user identifier placeholder.
    if not user_id and token:
        user_id = token

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """Get current user if logged in, else return None."""
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None

    try:
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalars().first()
        return user
    except Exception:
        return None


async def inject_user(
    request: Request,
    user=Depends(get_current_user_optional),
):
    """Inject user into request state. User can be None if not logged in."""
    request.state.user = user
