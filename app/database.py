# -*- coding: utf-8 -*-
"""
Database configuration module using SQLAlchemy ORM with async support.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)

# SQLite database URL with async driver (aiosqlite)
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    future=True,
    pool_pre_ping=True,  # Verify connections before using them
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)

# Base class for all ORM models
Base = declarative_base()


async def get_db_session():
    """
    Dependency for getting async database session.
    Used in FastAPI routes for database access.
    """
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
    """
    Initialize database by creating all tables defined in ORM models.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
        await seed_database()
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise


async def seed_database():
    """
    Seed the database with test data from JSON file if it's empty.
    """
    import json
    from models import User, Recipe, Ingredient, Tag, recipe_ingredients, recipe_tags

    async with AsyncSessionLocal() as session:
        try:
            # Check if data already exists
            result = await session.execute(text("SELECT COUNT(*) FROM recipes"))
            recipe_count = result.scalar()

            if recipe_count == 0:
                logger.info("Seeding database with test data...")

                # Load test data from JSON file
                with open("test_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Create ingredients
                ingredients = []
                for name in data["ingredients"]:
                    ingredient = Ingredient(name=name)
                    session.add(ingredient)
                    ingredients.append(ingredient)

                await session.flush()  # Get IDs

                # Create tags
                tags = []
                for name in data["tags"]:
                    tag = Tag(name=name)
                    session.add(tag)
                    tags.append(tag)

                await session.flush()

                # Create recipes
                recipes = []
                for recipe_data in data["recipes"]:
                    recipe = Recipe(
                        title=recipe_data["title"],
                        time_minutes=recipe_data["time_minutes"],
                        price=recipe_data["price"],
                        link=recipe_data["link"],
                        description=recipe_data["description"]
                    )
                    session.add(recipe)
                    recipes.append(recipe)

                await session.flush()  # Get recipe IDs

                # Add recipe-ingredient relationships
                for i, recipe_data in enumerate(data["recipes"]):
                    recipe = recipes[i]
                    for ing_data in recipe_data["ingredients"]:
                        await session.execute(
                            recipe_ingredients.insert().values(
                                recipe_id=recipe.id,
                                ingredient_id=ingredients[ing_data["index"]].id,
                                amount=ing_data["amount"],
                                unit=ing_data["unit"]
                            )
                        )

                # Add recipe-tag relationships
                for i, recipe_data in enumerate(data["recipes"]):
                    recipe = recipes[i]
                    for tag_idx in recipe_data["tags"]:
                        await session.execute(
                            recipe_tags.insert().values(
                                recipe_id=recipe.id,
                                tag_id=tags[tag_idx].id
                            )
                        )

                await session.commit()
                logger.info("Test data seeded successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding database: {str(e)}")
            raise


async def close_db():
    """Close database connection on application shutdown."""
    try:
        await engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")
