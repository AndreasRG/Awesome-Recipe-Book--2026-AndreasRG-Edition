# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from schemas import RecipeCreate
from services.recipes import list_recipes, get_recipe, create_recipe


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
    return recipe


@router.post("/", status_code=201)
async def recipe_create_route(data: RecipeCreate, db: AsyncSession = Depends(get_db_session)):
    recipe = await create_recipe(db, data)
    return {"id": recipe.id}