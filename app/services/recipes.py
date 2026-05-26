# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Ingredient, Recipe, Tag

# ---------------------------------------------------------
# Recipe Service Logic
# ---------------------------------------------------------

RECIPE_LOAD = [selectinload(Recipe.tags), selectinload(Recipe.ingredients)]


async def list_recipes(db: AsyncSession):
    result = await db.execute(select(Recipe).options(*RECIPE_LOAD))
    return result.scalars().unique().all()


async def get_recipe(db: AsyncSession, recipe_id: int):
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id).options(*RECIPE_LOAD)
    )
    return result.scalars().first()


async def create_recipe(
    db: AsyncSession,
    recipe_in,
    user_id: int | None = None,
    image=None,
):
    """
    Create a new recipe. Requires authentication.
    """

    if user_id is None:
        raise PermissionError("User must be logged in to create a recipe")

    new_recipe = Recipe(
        title=recipe_in.title,
        time_minutes=recipe_in.time_minutes,
        price=recipe_in.price,
        link=recipe_in.link,
        description=recipe_in.description,
        user_id=user_id,
    )

    if getattr(recipe_in, "tags", None):
        tag_rows = await db.execute(select(Tag).where(Tag.id.in_(recipe_in.tags)))
        new_recipe.tags = tag_rows.scalars().all()

    if getattr(recipe_in, "ingredients", None):
        ing_rows = await db.execute(
            select(Ingredient).where(Ingredient.id.in_(recipe_in.ingredients))
        )
        new_recipe.ingredients = ing_rows.scalars().all()

    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)

    return new_recipe
