# -*- coding: utf-8 -*-
"""
Database configuration module using SQLAlchemy ORM with async support.
"""

import json
import logging
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Use DATABASE_URL from environment (recommended)
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://recipe_user:admin123@27.0.0.6/recipe_db"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)

# Base ORM class
Base = declarative_base()


async def get_db_session():
    """Provide a database session to FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


async def init_db():
    """Create tables and seed database."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables created successfully")
        await seed_database()

    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise


async def seed_database():
    """Seed database with test data if empty."""
    from app.models import Ingredient, Recipe, Tag, recipe_ingredients, recipe_tags

    async with AsyncSessionLocal() as session:
        try:
            # Check if recipes already exist
            result = await session.execute(text("SELECT COUNT(*) FROM recipes"))
            recipe_count = result.scalar()

            if recipe_count == 0:
                logger.info("Seeding database with test data...")

                # Correct path inside Docker
                json_path = "/app/app/test_data.json"

                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Ingredients
                ingredients = []
                for name in data["ingredients"]:
                    obj = Ingredient(name=name)
                    session.add(obj)
                    ingredients.append(obj)

                await session.flush()

                # Tags
                tags = []
                for name in data["tags"]:
                    obj = Tag(name=name)
                    session.add(obj)
                    tags.append(obj)

                await session.flush()

                # Recipes
                recipes = []
                for r in data["recipes"]:
                    recipe = Recipe(
                        title=r["title"],
                        time_minutes=r["time_minutes"],
                        price=r["price"],
                        link=r["link"],
                        description=r["description"],
                    )
                    session.add(recipe)
                    recipes.append(recipe)

                await session.flush()

                # Recipe → Ingredients
                for i, r in enumerate(data["recipes"]):
                    recipe = recipes[i]
                    for ing in r["ingredients"]:
                        await session.execute(
                            recipe_ingredients.insert().values(
                                recipe_id=recipe.id,
                                ingredient_id=ingredients[ing["index"]].id,
                                amount=ing["amount"],
                                unit=ing["unit"],
                            )
                        )

                # Recipe → Tags
                for i, r in enumerate(data["recipes"]):
                    recipe = recipes[i]
                    for tag_idx in r["tags"]:
                        await session.execute(
                            recipe_tags.insert().values(
                                recipe_id=recipe.id,
                                tag_id=tags[tag_idx].id,
                            )
                        )

                await session.commit()
                logger.info("Test data seeded successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding database: {str(e)}")
            raise


async def close_db():
    """Close database connection on shutdown."""
    try:
        await engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")
