# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import init_db
from app.routers import pages, recipes, users  # <-- MOVED TO TOP (fixes E402)

# ---------------------------------------------------------
# App setup
# ---------------------------------------------------------

app = FastAPI(title="Recipe API (FastAPI ORM)")

# Templates (used by pages router)
templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------------
# Health Check Endpoint
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

app.include_router(pages.router)
app.include_router(recipes.router)
app.include_router(users.router)

# Enable Prometheus metrics
Instrumentator().instrument(app).expose(app)

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
        "tags_url": "/api/recipe/tags/",
    }


# ---------------------------------------------------------
# Run with python app.py
# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=False))
