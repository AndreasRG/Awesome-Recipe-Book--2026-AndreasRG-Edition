# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates

from database import get_db_session
from services.recipes import list_recipes, get_recipe


# ---------------------------------------------------------
# Home page (HTML)
# ---------------------------------------------------------

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def home(request: Request, db: AsyncSession = Depends(get_db_session)):
    recipes = await list_recipes(db)

    recipe_list = [
        {
            "id": r.id,
            "title": r.title,
            "time_minutes": r.time_minutes,
            "price": r.price,
            "link": r.link or "",
            "tags": [{"id": t.id, "name": t.name} for t in r.tags]
        }
        for r in recipes
    ]

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "recipes": recipe_list}
    )


# ---------------------------------------------------------
# Recipe detail (HTML)
# ---------------------------------------------------------

@router.get("/recipes/{id}/")
async def recipe_detail(id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    recipe = await get_recipe(db, id)

    if not recipe:
        return templates.TemplateResponse(
            "recipe_not_found.html",
            {"request": request},
            status_code=404
        )

    recipe_data = {
        "id": recipe.id,
        "title": recipe.title,
        "time_minutes": recipe.time_minutes,
        "price": recipe.price,
        "link": recipe.link or "",
        "description": recipe.description or "",
        "ingredients": [{"id": ing.id, "name": ing.name} for ing in recipe.ingredients],
        "tags": [{"id": t.id, "name": t.name} for t in recipe.tags]
    }

    return templates.TemplateResponse(
        "recipe_detail.html",
        {"request": request, "recipe": recipe_data}
    )