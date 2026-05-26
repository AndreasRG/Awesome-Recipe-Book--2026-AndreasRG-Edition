# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_login
from app.database import get_db_session
from app.dependencies import inject_user
from app.metrics import RECIPE_VIEWS_TOTAL, RECIPES_CREATED_TOTAL
from app.schemas import RecipeCreate
from app.services.recipes import (
    create_recipe,
    get_recipe,
    list_recipes,
)
from app.services.users import User, get_current_user

templates = Jinja2Templates(
    directory="app/templates", dependencies=[Depends(inject_user)]
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
    title: str = Form(...),
    time_minutes: int = Form(...),
    price: str = Form(...),
    link: str | None = Form(None),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    data = RecipeCreate(
        title=title,
        time_minutes=time_minutes,
        price=price,
        link=link,
        description=description,
    )

    await create_recipe(
        db=db,
        recipe_in=data,
        user_id=current_user.id,
        image=image,
    )

    return RedirectResponse("/recipes", status_code=303)
