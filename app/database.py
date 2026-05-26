# -*- coding: utf-8 -*-
"""
Database configuration module using SQLAlchemy ORM with async support.
"""

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
    """Seed database with built‑in data if empty."""
    from app.models import Ingredient, Recipe, Tag, recipe_ingredients, recipe_tags

    async with AsyncSessionLocal() as session:
        try:
            # Check if recipes already exist
            result = await session.execute(text("SELECT COUNT(*) FROM recipes"))
            recipe_count = result.scalar()

            if recipe_count > 0:
                return  # Already seeded

            logger.info("Seeding database with built‑in data...")

            # ---------------------------------------------------------
            # Permanent built‑in seed data (converted from test_data.json)
            # ---------------------------------------------------------

            ingredient_names = [
                "Spaghetti",
                "Eggs",
                "Pancetta",
                "Parmesan Cheese",
                "Black Pepper",
                "Salt",
                "Chicken Breast",
                "Breadcrumbs",
                "Mozzarella Cheese",
                "Tomato Sauce",
                "Olive Oil",
                "Garlic",
                "Penne Pasta",
                "Bell Peppers",
                "Zucchini",
                "Cherry Tomatoes",
                "Basil",
                "Butter",
                "Flour",
                "Salmon Fillet",
                "Lemon",
                "Dill",
            ]

            tag_names = [
                "Italian",
                "Quick",
                "Dinner",
                "Vegetarian",
                "Healthy",
                "Seafood",
            ]

            recipes_data = [
                {
                    "title": "Spaghetti Carbonara",
                    "time_minutes": 25,
                    "price": "12.50",
                    "link": "http://example.com/carbonara",
                    "description": (
                        "Step 1: Bring a large pot of salted water to boil and cook 400g spaghetti according to package directions.\n\n"
                        "Step 2: While pasta cooks, cut 200g pancetta into small cubes and fry in a large pan over medium heat until crispy (about 5 minutes).\n\n"
                        "Step 3: In a bowl, whisk together 4 large eggs, 100g grated Parmesan cheese, and plenty of black pepper.\n\n"
                        "Step 4: When pasta is ready, reserve 1 cup of pasta water, then drain the pasta.\n\n"
                        "Step 5: Remove the pan with pancetta from heat. Add the hot pasta to the pan and toss.\n\n"
                        "Step 6: Pour the egg mixture over the pasta and toss quickly. The heat from the pasta will cook the eggs. Add pasta water bit by bit if needed to create a creamy sauce.\n\n"
                        "Step 7: Serve immediately with extra Parmesan cheese and black pepper."
                    ),
                    "ingredients": [
                        {"index": 0, "amount": "400", "unit": "g"},
                        {"index": 1, "amount": "4", "unit": "large"},
                        {"index": 2, "amount": "200", "unit": "g"},
                        {"index": 3, "amount": "100", "unit": "g"},
                        {"index": 4, "amount": "1", "unit": "tsp"},
                        {"index": 5, "amount": "1", "unit": "tsp"},
                    ],
                    "tags": [0, 2],
                },
                {
                    "title": "Chicken Parmesan",
                    "time_minutes": 50,
                    "price": "18.00",
                    "link": "http://example.com/chicken-parm",
                    "description": (
                        "Step 1: Preheat oven to 200C (400F).\n\n"
                        "Step 2: Place 2 chicken breasts between plastic wrap and pound to 2cm thickness.\n\n"
                        "Step 3: Set up breading station: flour in one plate, 2 beaten eggs in another, and 150g breadcrumbs mixed with 50g Parmesan in a third.\n\n"
                        "Step 4: Season chicken with salt and pepper, then coat in flour, dip in egg, and press into breadcrumb mixture.\n\n"
                        "Step 5: Heat 3 tablespoons olive oil in a large oven-safe skillet over medium-high heat. Fry chicken until golden brown, about 4 minutes per side.\n\n"
                        "Step 6: Pour 300ml tomato sauce over the chicken, then top each breast with 100g sliced mozzarella.\n\n"
                        "Step 7: Transfer skillet to oven and bake for 15-20 minutes until cheese is melted and bubbly.\n\n"
                        "Step 8: Garnish with fresh basil and serve with pasta or salad."
                    ),
                    "ingredients": [
                        {"index": 6, "amount": "2", "unit": "pieces"},
                        {"index": 7, "amount": "150", "unit": "g"},
                        {"index": 8, "amount": "100", "unit": "g"},
                        {"index": 9, "amount": "300", "unit": "ml"},
                        {"index": 10, "amount": "3", "unit": "tbsp"},
                        {"index": 3, "amount": "50", "unit": "g"},
                        {"index": 1, "amount": "2", "unit": "large"},
                        {"index": 18, "amount": "100", "unit": "g"},
                        {"index": 16, "amount": "10", "unit": "leaves"},
                    ],
                    "tags": [0, 2],
                },
                {
                    "title": "Pasta Primavera",
                    "time_minutes": 30,
                    "price": "10.00",
                    "link": "http://example.com/primavera",
                    "description": (
                        "Step 1: Cook 350g penne pasta in salted boiling water according to package directions. Reserve 1 cup pasta water before draining.\n\n"
                        "Step 2: While pasta cooks, chop 1 red bell pepper, 1 zucchini into bite-sized pieces, and halve 200g cherry tomatoes.\n\n"
                        "Step 3: Heat 3 tablespoons olive oil in a large pan over medium-high heat. Add 3 minced garlic cloves and cook for 30 seconds.\n\n"
                        "Step 4: Add bell peppers and zucchini to the pan. Cook for 5-7 minutes until vegetables are tender.\n\n"
                        "Step 5: Add cherry tomatoes and cook for another 2-3 minutes until they start to soften.\n\n"
                        "Step 6: Add the drained pasta to the pan with vegetables. Toss everything together, adding pasta water as needed to create a light sauce.\n\n"
                        "Step 7: Season with salt and black pepper. Remove from heat and stir in fresh basil leaves.\n\n"
                        "Step 8: Serve hot with grated Parmesan cheese on top."
                    ),
                    "ingredients": [
                        {"index": 12, "amount": "350", "unit": "g"},
                        {"index": 13, "amount": "1", "unit": "piece"},
                        {"index": 14, "amount": "1", "unit": "piece"},
                        {"index": 15, "amount": "200", "unit": "g"},
                        {"index": 11, "amount": "3", "unit": "cloves"},
                        {"index": 10, "amount": "3", "unit": "tbsp"},
                        {"index": 16, "amount": "15", "unit": "leaves"},
                        {"index": 3, "amount": "50", "unit": "g"},
                    ],
                    "tags": [0, 1, 3, 4],
                },
                {
                    "title": "Garlic Butter Salmon",
                    "time_minutes": 20,
                    "price": "22.00",
                    "link": "http://example.com/salmon",
                    "description": (
                        "Step 1: Pat 4 salmon fillets (150g each) dry with paper towels and season both sides with salt and pepper.\n\n"
                        "Step 2: Heat 2 tablespoons olive oil in a large skillet over medium-high heat.\n\n"
                        "Step 3: Place salmon fillets skin-side up in the pan. Cook for 4-5 minutes until golden brown.\n\n"
                        "Step 4: Flip the salmon and cook for another 3-4 minutes.\n\n"
                        "Step 5: Reduce heat to medium and add 3 tablespoons butter, 4 minced garlic cloves, and juice of 1 lemon to the pan.\n\n"
                        "Step 6: Spoon the garlic butter sauce over the salmon repeatedly for 1-2 minutes.\n\n"
                        "Step 7: Remove from heat and sprinkle with fresh dill.\n\n"
                        "Step 8: Serve immediately with the pan sauce, accompanied by rice or vegetables."
                    ),
                    "ingredients": [
                        {"index": 19, "amount": "4", "unit": "fillets"},
                        {"index": 17, "amount": "3", "unit": "tbsp"},
                        {"index": 11, "amount": "4", "unit": "cloves"},
                        {"index": 20, "amount": "1", "unit": "piece"},
                        {"index": 21, "amount": "2", "unit": "tbsp"},
                        {"index": 10, "amount": "2", "unit": "tbsp"},
                    ],
                    "tags": [1, 2, 4, 5],
                },
            ]

            # ---------------------------------------------------------
            # Insert ingredients
            # ---------------------------------------------------------
            ingredients = []
            for name in ingredient_names:
                obj = Ingredient(name=name)
                session.add(obj)
                ingredients.append(obj)

            await session.flush()

            # ---------------------------------------------------------
            # Insert tags
            # ---------------------------------------------------------
            tags = []
            for name in tag_names:
                obj = Tag(name=name)
                session.add(obj)
                tags.append(obj)

            await session.flush()

            # ---------------------------------------------------------
            # Insert recipes
            # ---------------------------------------------------------
            recipes = []
            for r in recipes_data:
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

            # ---------------------------------------------------------
            # Recipe → Ingredients
            # ---------------------------------------------------------
            for i, r in enumerate(recipes_data):
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

            # ---------------------------------------------------------
            # Recipe → Tags
            # ---------------------------------------------------------
            for i, r in enumerate(recipes_data):
                recipe = recipes[i]
                for tag_idx in r["tags"]:
                    await session.execute(
                        recipe_tags.insert().values(
                            recipe_id=recipe.id,
                            tag_id=tags[tag_idx].id,
                        )
                    )

            await session.commit()
            logger.info("Built‑in data seeded successfully")

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
