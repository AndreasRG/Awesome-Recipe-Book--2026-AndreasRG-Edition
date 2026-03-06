# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import Recipe, Ingredient, Tag


# ---------------------------------------------------------
# Recipe Service Logic
# ---------------------------------------------------------

# Eager-loading configuration reused across queries
RECIPE_LOAD = [
    selectinload(Recipe.tags),
    selectinload(Recipe.ingredients)
]


async def list_recipes(db: AsyncSession):
    """Return all recipes with tags + ingredients eagerly loaded."""
    result = await db.execute(
        select(Recipe).options(*RECIPE_LOAD)
    )
    return result.scalars().unique().all()


async def get_recipe(db: AsyncSession, recipe_id: int):
    """Return a single recipe by ID with relationships loaded."""
    result = await db.execute(
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(*RECIPE_LOAD)
    )
    return result.scalars().first()


async def create_recipe(db: AsyncSession, data):
    """Create a new recipe and attach tags + ingredients."""
    new_recipe = Recipe(
        title=data.title,
        time_minutes=data.time_minutes,
        price=data.price,
        link=data.link,
        description=data.description
    )

    # Attach tags
    if data.tags:
        tag_rows = await db.execute(
            select(Tag).where(Tag.id.in_(data.tags))
        )
        new_recipe.tags = tag_rows.scalars().all()

    # Attach ingredients
    if data.ingredients:
        ing_rows = await db.execute(
            select(Ingredient).where(Ingredient.id.in_(data.ingredients))
        )
        new_recipe.ingredients = ing_rows.scalars().all()

    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)

    return new_recipe
