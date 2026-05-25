# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.metrics import RECIPE_VIEWS_TOTAL, RECIPES_CREATED_TOTAL
from app.schemas import RecipeCreate
from app.services.recipes import create_recipe, get_recipe, list_recipes

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
