# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.metrics import LOGIN_ATTEMPTS_TOTAL, USER_SIGNUPS_TOTAL
from app.schemas import TokenCreate, UserCreate, UserUpdate
from app.services.users import (
    authenticate_user,
    create_user,
    login_user,
    register_user_from_form,
)

templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------------
# API ROUTER (JSON)
# ---------------------------------------------------------

api = APIRouter(prefix="/api/user", tags=["users"])


@api.post("/create/", status_code=201)
async def user_create_route(
    data: UserCreate, db: AsyncSession = Depends(get_db_session)
):
    """Create a new user from JSON payload."""
    try:
        user = await create_user(db, data)
        USER_SIGNUPS_TOTAL.inc()
        return {"id": user.id, "email": user.email, "name": user.name}
    except Exception as err:
        raise HTTPException(status_code=400, detail="Email already exists") from err


@api.get("/me/")
async def user_me_route():
    return {"email": "user@example.com", "name": "Example User"}


@api.put("/me/")
async def user_me_update_route(data: UserUpdate):
    return {
        "email": data.email or "user@example.com",
        "name": data.name or "Example User",
    }


@api.patch("/me/")
async def user_me_partial_update_route(data: UserUpdate):
    return {
        "email": data.email or "user@example.com",
        "name": data.name or "Example User",
    }


@api.post("/token/")
async def user_token_route(
    data: TokenCreate, db: AsyncSession = Depends(get_db_session)
):
    LOGIN_ATTEMPTS_TOTAL.inc()

    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"email": user.email, "token": "placeholder_jwt_token"}


# ---------------------------------------------------------
# HTML ROUTER (Pages)
# ---------------------------------------------------------

pages = APIRouter(prefix="/auth")


@pages.get("/login")
async def login_page(request: Request):
    """Render the login page for browser users."""
    return templates.TemplateResponse("login.html", {"request": request})


@pages.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
):
    user = await login_user(db, email, password)

    if not user:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid email or password"}
        )

    response = RedirectResponse("/", status_code=302)
    response.set_cookie("user_id", str(user.id))
    return response


@pages.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@pages.post("/signup")
async def signup_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        await register_user_from_form(db, email, password, name)
    except Exception:
        return templates.TemplateResponse(
            "signup.html", {"request": request, "error": "Email already exists"}
        )

    response = RedirectResponse("/auth/login", status_code=302)
    return response


@pages.get("/logout")
async def logout():
    """Logout user by clearing the user_id cookie."""
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("user_id")
    return response
