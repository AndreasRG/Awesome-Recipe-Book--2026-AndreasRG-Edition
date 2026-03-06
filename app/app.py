# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routers import pages, recipes, users
from database import init_db


# ---------------------------------------------------------
# App setup
# ---------------------------------------------------------

app = FastAPI(title="Recipe API (FastAPI ORM)")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates (used by pages router)
templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------
# Include Routers
# ---------------------------------------------------------

app.include_router(pages.router)
app.include_router(recipes.router)
app.include_router(users.router)


# ---------------------------------------------------------
# Startup: Create tables
# ---------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    await init_db()


# ---------------------------------------------------------
# API Overview
# ---------------------------------------------------------

@app.get("/api")
async def api_overview():
    return {
        "create_user_url": "/api/user/create/",
        "current_user_url": "/api/user/me/",
        "user_token_url": "/api/user/token/",
        "recipes_url": "/api/recipe/recipes/",
        "recipe_url": "/api/recipe/recipes/{id}/",
        "ingredients_url": "/api/recipe/ingredients/",
        "tags_url": "/api/recipe/tags/"
    }


# ---------------------------------------------------------
# Run with python app.py
# ---------------------------------------------------------

import uvicorn
import asyncio

if __name__ == "__main__":
    asyncio.run(
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=5000,
            reload=False
        )
    )
