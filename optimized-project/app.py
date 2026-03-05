# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Recipe API (FastAPI)")
DATABASE = "app.db"
templates = Jinja2Templates(directory="templates")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None

class TokenCreate(BaseModel):
    email: str
    password: str

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

## SQL doublication could be reducedby using ORM.

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            time_minutes INTEGER NOT NULL,
            price TEXT NOT NULL,
            link TEXT,
            description TEXT,
            image TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            recipe_id INTEGER,
            ingredient_id INTEGER,
            amount TEXT,
            unit TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipe_tags (
            recipe_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
    ''')

## No roleback mechanism in case of failure. Data integrity issues are likely or partial datasets.

    cursor.execute('SELECT COUNT(*) FROM recipes')
    recipe_count = cursor.fetchone()[0]

    if recipe_count == 0:
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Spaghetti')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Eggs')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Pancetta')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Parmesan Cheese')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Black Pepper')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Salt')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Chicken Breast')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Breadcrumbs')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Mozzarella Cheese')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Tomato Sauce')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Olive Oil')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Garlic')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Penne Pasta')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Bell Peppers')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Zucchini')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Cherry Tomatoes')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Basil')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Butter')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Flour')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Salmon Fillet')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Lemon')")
        cursor.execute("INSERT INTO ingredients (name) VALUES ('Dill')")

        cursor.execute("INSERT INTO tags (name) VALUES ('Italian')")
        cursor.execute("INSERT INTO tags (name) VALUES ('Quick')")
        cursor.execute("INSERT INTO tags (name) VALUES ('Dinner')")
        cursor.execute("INSERT INTO tags (name) VALUES ('Vegetarian')")
        cursor.execute("INSERT INTO tags (name) VALUES ('Healthy')")
        cursor.execute("INSERT INTO tags (name) VALUES ('Seafood')")

        cursor.execute("""
            INSERT INTO recipes (title, time_minutes, price, link, description)
            VALUES ('Spaghetti Carbonara', 25, '12.50', 'http://example.com/carbonara',
            'Step 1: Bring a large pot of salted water to boil and cook 400g spaghetti according to package directions.

Step 2: While pasta cooks, cut 200g pancetta into small cubes and fry in a large pan over medium heat until crispy (about 5 minutes).

Step 3: In a bowl, whisk together 4 large eggs, 100g grated Parmesan cheese, and plenty of black pepper.

Step 4: When pasta is ready, reserve 1 cup of pasta water, then drain the pasta.

Step 5: Remove the pan with pancetta from heat. Add the hot pasta to the pan and toss.

Step 6: Pour the egg mixture over the pasta and toss quickly. The heat from the pasta will cook the eggs. Add pasta water bit by bit if needed to create a creamy sauce.

Step 7: Serve immediately with extra Parmesan cheese and black pepper.')
        """)
        recipe1_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO recipes (title, time_minutes, price, link, description)
            VALUES ('Chicken Parmesan', 50, '18.00', 'http://example.com/chicken-parm',
            'Step 1: Preheat oven to 200C (400F).

Step 2: Place 2 chicken breasts between plastic wrap and pound to 2cm thickness.

Step 3: Set up breading station: flour in one plate, 2 beaten eggs in another, and 150g breadcrumbs mixed with 50g Parmesan in a third.

Step 4: Season chicken with salt and pepper, then coat in flour, dip in egg, and press into breadcrumb mixture.

Step 5: Heat 3 tablespoons olive oil in a large oven-safe skillet over medium-high heat. Fry chicken until golden brown, about 4 minutes per side.

Step 6: Pour 300ml tomato sauce over the chicken, then top each breast with 100g sliced mozzarella.

Step 7: Transfer skillet to oven and bake for 15-20 minutes until cheese is melted and bubbly.

Step 8: Garnish with fresh basil and serve with pasta or salad.')
        """)
        recipe2_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO recipes (title, time_minutes, price, link, description)
            VALUES ('Pasta Primavera', 30, '10.00', 'http://example.com/primavera',
            'Step 1: Cook 350g penne pasta in salted boiling water according to package directions. Reserve 1 cup pasta water before draining.

Step 2: While pasta cooks, chop 1 red bell pepper, 1 zucchini into bite-sized pieces, and halve 200g cherry tomatoes.

Step 3: Heat 3 tablespoons olive oil in a large pan over medium-high heat. Add 3 minced garlic cloves and cook for 30 seconds.

Step 4: Add bell peppers and zucchini to the pan. Cook for 5-7 minutes until vegetables are tender.

Step 5: Add cherry tomatoes and cook for another 2-3 minutes until they start to soften.

Step 6: Add the drained pasta to the pan with vegetables. Toss everything together, adding pasta water as needed to create a light sauce.

Step 7: Season with salt and black pepper. Remove from heat and stir in fresh basil leaves.

Step 8: Serve hot with grated Parmesan cheese on top.')
        """)
        recipe3_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO recipes (title, time_minutes, price, link, description)
            VALUES ('Garlic Butter Salmon', 20, '22.00', 'http://example.com/salmon',
            'Step 1: Pat 4 salmon fillets (150g each) dry with paper towels and season both sides with salt and pepper.

Step 2: Heat 2 tablespoons olive oil in a large skillet over medium-high heat.

Step 3: Place salmon fillets skin-side up in the pan. Cook for 4-5 minutes until golden brown.

Step 4: Flip the salmon and cook for another 3-4 minutes.

Step 5: Reduce heat to medium and add 3 tablespoons butter, 4 minced garlic cloves, and juice of 1 lemon to the pan.

Step 6: Spoon the garlic butter sauce over the salmon repeatedly for 1-2 minutes.

Step 7: Remove from heat and sprinkle with fresh dill.

Step 8: Serve immediately with the pan sauce, accompanied by rice or vegetables.')
        """)
        recipe4_id = cursor.lastrowid

        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe1_id, 1, '400', 'g'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe1_id, 2, '4', 'large'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe1_id, 3, '200', 'g'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe1_id, 4, '100', 'g'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe1_id, 5, '1', 'tsp'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe1_id, 6, '1', 'tsp'))

        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe2_id, 7, '2', 'pieces'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe2_id, 8, '150', 'g'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe2_id, 9, '100', 'g'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe2_id, 10, '300', 'ml'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe2_id, 11, '3', 'tbsp'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe2_id, 4, '50', 'g'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe2_id, 2, '2', 'large'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe2_id, 19, '100', 'g'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe2_id, 17, '10', 'leaves'))

        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe3_id, 13, '350', 'g'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe3_id, 14, '1', 'piece'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe3_id, 15, '1', 'piece'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe3_id, 16, '200', 'g'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe3_id, 12, '3', 'cloves'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe3_id, 11, '3', 'tbsp'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe3_id, 17, '15', 'leaves'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe3_id, 4, '50', 'g'))

        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe4_id, 20, '4', 'fillets'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe4_id, 18, '3', 'tbsp'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe4_id, 12, '4', 'cloves'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe4_id, 21, '1', 'piece'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe4_id, 22, '2', 'tbsp'))
        cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)', (recipe4_id, 11, '2', 'tbsp'))

        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe1_id, 1))
        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe1_id, 3))

        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe2_id, 1))
        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe2_id, 3))

        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe3_id, 1))
        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe3_id, 2))
        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe3_id, 4))
        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe3_id, 5))

        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe4_id, 2))
        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe4_id, 3))
        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe4_id, 5))
        cursor.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (recipe4_id, 6))

    conn.commit()
    conn.close()


## Risc of SQL injection in the following routes: GET /, GET /recipes/<int:id>/, GET /api/recipe/recipes/<int:id>/, GET /api/recipe/ingredients/, GET /api/recipe/tags/

# -----------------------------
# Home route (GET /)
# -----------------------------
@app.get("/")
async def home(request: Request):
    print("Route invoked: GET /")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, time_minutes, price, link FROM recipes")
    recipes = cursor.fetchall()

    recipes_with_tags = []
    for recipe in recipes:
        cursor.execute("""
            SELECT t.id, t.name FROM tags t
            JOIN recipe_tags rt ON t.id = rt.tag_id
            WHERE rt.recipe_id = ?
        """, (recipe["id"],))
        recipe_tags = cursor.fetchall()

        recipes_with_tags.append({
            "id": recipe["id"],
            "title": recipe["title"],
            "time_minutes": recipe["time_minutes"],
            "price": recipe["price"],
            "link": recipe["link"] or "",
            "tags": [{"id": t["id"], "name": t["name"]} for t in recipe_tags]
        })

    conn.close()

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "recipes": recipes_with_tags}
    )


# -----------------------------
# Recipe detail route (GET /recipes/{id}/)
# -----------------------------
@app.get("/recipes/{id}/")
async def recipe_detail(id: int, request: Request):
    print("Route invoked: GET /recipes/<id>/")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, time_minutes, price, link, description FROM recipes WHERE id = ?",
        (id,)
    )
    recipe = cursor.fetchone()

    if recipe is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")

    cursor.execute("""
        SELECT i.id, i.name, ri.amount, ri.unit FROM ingredients i
        JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
        WHERE ri.recipe_id = ?
    """, (id,))
    recipe_ingredients = cursor.fetchall()

    cursor.execute("""
        SELECT t.id, t.name FROM tags t
        JOIN recipe_tags rt ON t.id = rt.tag_id
        WHERE rt.recipe_id = ?
    """, (id,))
    recipe_tags = cursor.fetchall()

    conn.close()

    recipe_data = {
        "id": recipe["id"],
        "title": recipe["title"],
        "time_minutes": recipe["time_minutes"],
        "price": recipe["price"],
        "link": recipe["link"] or "",
        "description": recipe["description"] or "",
        "ingredients": [
            {"id": ing["id"], "name": ing["name"], "amount": ing["amount"], "unit": ing["unit"]}
            for ing in recipe_ingredients
        ],
        "tags": [{"id": tag["id"], "name": tag["name"]} for tag in recipe_tags]
    }

    return templates.TemplateResponse(
        "recipe_detail.html",
        {"request": request, "recipe": recipe_data}
    )


# -----------------------------
# API overview route (GET /api)
# -----------------------------
@app.get("/api")
async def api_overview():
    print("Route invoked: GET /api")
    routes = {
        "create_user_url": "http://localhost:5000/api/user/create/",
        "current_user_url": "http://localhost:5000/api/user/me/",
        "user_token_url": "http://localhost:5000/api/user/token/",
        "recipes_url": "http://localhost:5000/api/recipe/recipes/{?ingredients,tags}",
        "recipe_url": "http://localhost:5000/api/recipe/recipes/{id}/",
        "recipe_image_url": "http://localhost:5000/api/recipe/recipes/{id}/upload-image/",
        "ingredients_url": "http://localhost:5000/api/recipe/ingredients/{?assigned_only}",
        "ingredient_url": "http://localhost:5000/api/recipe/ingredients/{id}/",
        "tags_url": "http://localhost:5000/api/recipe/tags/{?assigned_only}",
        "tag_url": "http://localhost:5000/api/recipe/tags/{id}/"
    }
    return JSONResponse(routes)

## User creation and authentication routes are not secure. Data leaks and hack-attacks are likely. Also there is some missing authentication and authorization logic in the following routes: GET /api/user/me/, PUT /api/user/me/, PATCH /api/user/me/, POST /api/user/token/, GET /api/recipe/recipes/, POST /api/recipe/recipes/, GET /api/recipe/recipes/<int:id>/, PUT /api/recipe/recipes/<int:id>/, PATCH /api/recipe/recipes/<int:id>/, DELETE /api/recipe/recipes/<int:id>/, POST /api/recipe/recipes/<int:id>/upload-image/, GET /api/recipe/ingredients/, PUT /api/recipe/ingredients/<int:id>/, PATCH /api/recipe/ingredients/<int:id>/, DELETE /api/recipe/ingredients/<int:id>/, GET /api/recipe/tags/, PUT /api/recipe/tags/<int:id>/, PATCH /api/recipe/tags/<int:id>/, DELETE /api/recipe/tags/<int:id>/
## Missing api authentication and authorization logic is a critical security issue that should be addressed before deploying this application. No input control.
## Missing error handling

@app.post('/api/user/create/')
async def user_create(user: UserCreate):
    print('Route invoked: POST /api/user/create/')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
        (user.email, user.password, user.name)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return JSONResponse(content={
        'email': user.email,
        'name': user.name
    }, status_code=201)

@app.get('/api/user/me/')
async def user_me_retrieve():
    print('Route invoked: GET /api/user/me/')
    return JSONResponse(content={
        'email': 'user@example.com',
        'name': 'Example User'
    }, status_code=200)

@app.put('/api/user/me/')
async def user_me_update(user: UserUpdate):
    print('Route invoked: PUT /api/user/me/')
    return JSONResponse(content={
        'email': user.email or 'user@example.com',
        'name': user.name or 'Example User'
    }, status_code=200)

@app.patch('/api/user/me/')
async def user_me_partial_update(user: UserUpdate):
    print('Route invoked: PATCH /api/user/me/')
    response = {}
    if user.email:
        response['email'] = user.email
    else:
        response['email'] = 'user@example.com'

    if user.name:
        response['name'] = user.name
    else:
        response['name'] = 'Example User'

    return JSONResponse(content=response, status_code=200)

@app.post('/api/user/token/')
async def user_token_create(token: TokenCreate):
    print('Route invoked: POST /api/user/token/')
    return JSONResponse(content={
        'email': token.email,
        'password': token.password
    }, status_code=200)

@app.get('/api/recipe/recipes/')
async def recipe_recipes_list(ingredients: Optional[str] = Query(None), tags: Optional[str] = Query(None)):
    print('Route invoked: GET /api/recipe/recipes/')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, time_minutes, price, link FROM recipes')
    recipes = cursor.fetchall()

    result = []
    for recipe in recipes:
        cursor.execute('''
            SELECT i.id, i.name, ri.amount, ri.unit FROM ingredients i
            JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
            WHERE ri.recipe_id = ?
        ''', (recipe['id'],))
        recipe_ingredients = cursor.fetchall()

        cursor.execute('''
            SELECT t.id, t.name FROM tags t
            JOIN recipe_tags rt ON t.id = rt.tag_id
            WHERE rt.recipe_id = ?
        ''', (recipe['id'],))
        recipe_tags = cursor.fetchall()

        result.append({
            'id': recipe['id'],
            'title': recipe['title'],
            'time_minutes': recipe['time_minutes'],
            'price': recipe['price'],
            'link': recipe['link'] or '',
            'ingredients': [{'id': ing['id'], 'name': ing['name'], 'amount': ing['amount'], 'unit': ing['unit']} for ing in recipe_ingredients],
            'tags': [{'id': tag['id'], 'name': tag['name']} for tag in recipe_tags]
        })

    conn.close()
    return JSONResponse(content=result, status_code=200)

@app.post('/api/recipe/recipes/')
async def recipe_recipes_create(recipe: dict):
    print('Route invoked: POST /api/recipe/recipes/')
    return JSONResponse(content={
        'id': 1,
        'title': recipe.get('title'),
        'time_minutes': recipe.get('time_minutes'),
        'price': recipe.get('price'),
        'link': recipe.get('link', ''),
        'tags': recipe.get('tags', []),
        'ingredients': recipe.get('ingredients', []),
        'description': recipe.get('description', '')
    }, status_code=201)

@app.get('/api/recipe/recipes/{id}/')
async def recipe_recipes_retrieve(id: int):
    print('Route invoked: GET /api/recipe/recipes/{id}/')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, time_minutes, price, link, description FROM recipes WHERE id = ?', (id,))
    recipe = cursor.fetchone()

    if not recipe:
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")

    cursor.execute('''
        SELECT i.id, i.name, ri.amount, ri.unit FROM ingredients i
        JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
        WHERE ri.recipe_id = ?
    ''', (id,))
    recipe_ingredients = cursor.fetchall()

    cursor.execute('''
        SELECT t.id, t.name FROM tags t
        JOIN recipe_tags rt ON t.id = rt.tag_id
        WHERE rt.recipe_id = ?
    ''', (id,))
    recipe_tags = cursor.fetchall()

    conn.close()

    return JSONResponse(content={
        'id': recipe['id'],
        'title': recipe['title'],
        'time_minutes': recipe['time_minutes'],
        'price': recipe['price'],
        'link': recipe['link'] or '',
        'description': recipe['description'] or '',
        'ingredients': [{'id': ing['id'], 'name': ing['name'], 'amount': ing['amount'], 'unit': ing['unit']} for ing in recipe_ingredients],
        'tags': [{'id': tag['id'], 'name': tag['name']} for tag in recipe_tags]
    }, status_code=200)

@app.put('/api/recipe/recipes/{id}/')
async def recipe_recipes_update(id: int, recipe: dict):
    print('Route invoked: PUT /api/recipe/recipes/{id}/')
    return JSONResponse(content={
        'id': id,
        'title': recipe.get('title'),
        'time_minutes': recipe.get('time_minutes'),
        'price': recipe.get('price'),
        'link': recipe.get('link', ''),
        'tags': recipe.get('tags', []),
        'ingredients': recipe.get('ingredients', []),
        'description': recipe.get('description', '')
    }, status_code=200)

@app.patch('/api/recipe/recipes/{id}/')
async def recipe_recipes_partial_update(id: int, recipe: dict):
    print('Route invoked: PATCH /api/recipe/recipes/{id}/')
    response = {
        'id': id,
        'title': recipe.get('title', 'Sample Recipe'),
        'time_minutes': recipe.get('time_minutes', 30),
        'price': recipe.get('price', '10.00'),
        'link': recipe.get('link', ''),
        'tags': recipe.get('tags', []),
        'ingredients': recipe.get('ingredients', []),
        'description': recipe.get('description', '')
    }

    return JSONResponse(content=response, status_code=200)

@app.delete('/api/recipe/recipes/{id}/')
async def recipe_recipes_destroy(id: int):
    print('Route invoked: DELETE /api/recipe/recipes/{id}/')
    return JSONResponse(content='', status_code=204)

@app.post('/api/recipe/recipes/{id}/upload-image/')
async def recipe_recipes_upload_image(id: int):
    print('Route invoked: POST /api/recipe/recipes/{id}/upload-image/')
    return JSONResponse(content={
        'id': id,
        'image': 'http://example.com/image.jpg'
    }, status_code=200)

@app.get('/api/recipe/ingredients/')
async def recipe_ingredients_list(assigned_only: Optional[str] = Query(None)):
    print('Route invoked: GET /api/recipe/ingredients/')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM ingredients')
    ingredients = cursor.fetchall()
    conn.close()

    result = [{'id': ing['id'], 'name': ing['name']} for ing in ingredients]
    return JSONResponse(content=result, status_code=200)

@app.put('/api/recipe/ingredients/{id}/')
async def recipe_ingredients_update(id: int, ingredient: dict):
    print('Route invoked: PUT /api/recipe/ingredients/{id}/')
    return JSONResponse(content={
        'id': id,
        'name': ingredient.get('name')
    }, status_code=200)

@app.patch('/api/recipe/ingredients/{id}/')
async def recipe_ingredients_partial_update(id: int, ingredient: dict):
    print('Route invoked: PATCH /api/recipe/ingredients/{id}/')
    return JSONResponse(content={
        'id': id,
        'name': ingredient.get('name', 'Sample Ingredient')
    }, status_code=200)

@app.delete('/api/recipe/ingredients/{id}/')
async def recipe_ingredients_destroy(id: int):
    print('Route invoked: DELETE /api/recipe/ingredients/{id}/')
    return JSONResponse(content='', status_code=204)

@app.get('/api/recipe/tags/')
async def recipe_tags_list(assigned_only: Optional[str] = Query(None)):
    print('Route invoked: GET /api/recipe/tags/')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM tags')
    tags = cursor.fetchall()
    conn.close()

    result = [{'id': tag['id'], 'name': tag['name']} for tag in tags]
    return JSONResponse(content=result, status_code=200)

@app.put('/api/recipe/tags/{id}/')
async def recipe_tags_update(id: int, tag: dict):
    print('Route invoked: PUT /api/recipe/tags/{id}/')
    return JSONResponse(content={
        'id': id,
        'name': tag.get('name')
    }, status_code=200)

@app.patch('/api/recipe/tags/{id}/')
async def recipe_tags_partial_update(id: int, tag: dict):
    print('Route invoked: PATCH /api/recipe/tags/{id}/')
    return JSONResponse(content={
        'id': id,
        'name': tag.get('name', 'Sample Tag')
    }, status_code=200)

@app.delete('/api/recipe/tags/{id}/')
async def recipe_tags_destroy(id: int):
    print('Route invoked: DELETE /api/recipe/tags/{id}/')
    return JSONResponse(content='', status_code=204)

## debug mode should be off in releases.

if __name__ == '__main__':
    init_db()
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
