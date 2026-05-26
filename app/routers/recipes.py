# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_login
from app.database import get_db_session
from app.dependencies import get_current_user, inject_user
from app.metrics import RECIPE_VIEWS_TOTAL, RECIPES_CREATED_TOTAL
from app.models import User
from app.schemas import RecipeCreate
from app.services.recipes import (
    create_recipe,
    get_recipe,
    list_recipes,
)

templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------------
# API ROUTER (JSON)
# ---------------------------------------------------------

api = APIRouter(prefix="/api/recipe/recipes", tags=["recipes"])


@api.get("/")
async def recipe_list_route(db: AsyncSession = Depends(get_db_session)):
    return await list_recipes(db)


@api.get("/{id}/")
async def recipe_detail_route(id: int, db: AsyncSession = Depends(get_db_session)):
    recipe = await get_recipe(db, id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    RECIPE_VIEWS_TOTAL.inc()
    return recipe


@api.post("/", status_code=201)
async def recipe_create_route(
    data: RecipeCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    recipe = await create_recipe(db, data, user_id=current_user.id)
    RECIPES_CREATED_TOTAL.inc()
    return {"id": recipe.id}


# ---------------------------------------------------------
# HTML ROUTER (Pages)
# ---------------------------------------------------------

pages = APIRouter(prefix="/recipes")


@pages.get("/", dependencies=[Depends(inject_user)])
async def recipes_page(request: Request, db: AsyncSession = Depends(get_db_session)):
    recipes = await list_recipes(db)
    return templates.TemplateResponse(
        "recipes.html",
        {"request": request, "recipes": recipes},
    )


@pages.get("/new")
async def new_recipe_page(request: Request):
    auth = require_login(request)
    if auth:
        # Return a tiny HTML page that triggers a browser alert + redirect
        return HTMLResponse(
            """
            <script>
                alert("You are not logged in, please login and try again!");
                window.location.href = "/auth/login";
            </script>
            """,
            status_code=401,
        )

    return templates.TemplateResponse("new_recipe.html", {"request": request})


@pages.post("/new")
async def new_recipe_submit(
    request: Request,
    title: str = Form(...),
    time_minutes: int = Form(...),
    price: str = Form(...),
    link: str | None = Form(None),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    data = RecipeCreate(
        title=title,
        time_minutes=time_minutes,
        price=price,
        link=link,
        description=description,
    )

    try:
        await create_recipe(
            db=db,
            recipe_in=data,
            user_id=current_user.id,
            image=image,
        )
    except PermissionError:
        return HTMLResponse(
            """
            <script>
                alert("You are not logged in, please login and try again!");
                window.location.href = "/auth/login";
            </script>
            """,
            status_code=401,
        )

    return RedirectResponse("/recipes", status_code=303)
