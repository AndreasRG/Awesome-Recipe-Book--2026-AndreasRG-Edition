from fastapi import Depends, Request

from app.services.users import get_current_user


async def inject_user(request: Request, user=Depends(get_current_user)):
    request.state.user = user
