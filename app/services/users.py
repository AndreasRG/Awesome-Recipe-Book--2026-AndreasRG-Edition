# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import User


# ---------------------------------------------------------
# Users Service Logic
# ---------------------------------------------------------

async def create_user(db: AsyncSession, data):
    """Create a new user."""
    new_user = User(
        email=data.email,
        password=data.password,
        name=data.name
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def authenticate_user(db: AsyncSession, email: str, password: str):
    """Return user if email/password match, else None."""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalars().first()

    if not user or user.password != password:
        return None

    return user