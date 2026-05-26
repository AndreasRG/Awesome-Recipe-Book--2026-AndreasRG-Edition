# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator

# Import router modules ONLY (Ruff requires imports at top)
import app.routers.pages as pages
import app.routers.recipes as recipes
import app.routers.users as users
from app.database import init_db

# ---------------------------------------------------------
# App setup
# ---------------------------------------------------------

app = FastAPI(title="Recipe API (FastAPI ORM)")

# Templates must exist BEFORE routers use them
templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------
# Static files
# ---------------------------------------------------------

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ---------------------------------------------------------
# Include Routers
# ---------------------------------------------------------

# Pages router (home + recipe detail)
app.include_router(pages.router)

# Recipes routers
app.include_router(recipes.api)
app.include_router(recipes.pages)

# Users routers
app.include_router(users.api)
app.include_router(users.pages)

# Prometheus
Instrumentator().instrument(app).expose(app)

# ---------------------------------------------------------
# Startup
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
        "tags_url": "/api/recipe/tags/",
    }


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=False))
