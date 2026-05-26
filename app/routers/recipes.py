# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_login
from app.database import get_db_session
from app.main import templates
from app.metrics import RECIPE_VIEWS_TOTAL, RECIPES_CREATED_TOTAL
from app.schemas import RecipeCreate
from app.services.recipes import (
    create_recipe,
    create_recipe_from_form,
    get_recipe,
    list_recipes,
)

# ---------------------------------------------------------
# Recipe API (ORM)
# ---------------------------------------------------------

router = APIRouter(prefix="/api/recipe/recipes", tags=["recipes"])


@router.get("/")
async def recipe_list_route(db: AsyncSession = Depends(get_db_session)):
    return await list_recipes(db)


@router.get("/{id}/")
async def recipe_detail_route(id: int, db: AsyncSession = Depends(get_db_session)):
    recipe = await get_recipe(db, id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    RECIPE_VIEWS_TOTAL.inc()

    return recipe


@router.post("/", status_code=201)
async def recipe_create_route(
    data: RecipeCreate, db: AsyncSession = Depends(get_db_session)
):
    recipe = await create_recipe(db, data)

    RECIPES_CREATED_TOTAL.inc()

    return {"id": recipe.id}


router = APIRouter(prefix="/recipes")


@router.get("/new")
async def new_recipe_page(request: Request):
    auth = require_login(request)
    if auth:
        return auth

    return templates.TemplateResponse("new_recipe.html", {"request": request})


@router.post("/new")
async def new_recipe_submit(
    request: Request,
    title: str = Form(...),
    time_minutes: int = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
):
    auth = require_login(request)
    if auth:
        return auth

    await create_recipe_from_form(db, title, time_minutes, price, description)
    return RedirectResponse("/", status_code=302)
