# Understanding the Routers Layer

## Overview:
Routers define the public interface of the application. They receive HTTP requests, validate input using Pydantic schemas, call service functions, and return responses. Routers do not contain business logic or database operations. Instead, they act as the “API layer” or “presentation layer” of the backend.

### Router Groups:

1 - Pages Router

- Handles HTML endpoints.

- Renders templates such as home.html and recipe_detail.html.

- Calls recipe services to fetch data for the UI.

- Does not return JSON.

2 - Recipes Router

- Handles REST API endpoints for recipes.

- Supports listing recipes, retrieving a single recipe, and creating new recipes.

- Uses Pydantic schemas for validation.

- Calls recipe service functions for all database operations.

3 - Users Router

- Handles user-related API endpoints.

- Supports user creation, user profile endpoints, and token creation.

- Delegates all database operations to the user service.

### How endpoints work inside routers:

Routers define the actual HTTP endpoints of the application. Each endpoint corresponds to a specific HTTP method and path. All endpoints use the base URL "http://localhost:5000". For example:

- GET /api/recipe/recipes/

- GET /api/recipe/recipes/{id}/

- POST /api/recipe/recipes/

- GET / (home page)

- GET /recipes/{id}/ (HTML detail page)

When a request reaches a router, the router performs three tasks:

- It validates incoming data using Pydantic schemas (for POST/PUT/PATCH requests).

- It calls the appropriate service function to perform the actual logic.

- It returns the result as JSON or renders an HTML template.

Routers do not contain business logic. They do not talk directly to the database. They only coordinate the flow between the client and the services layer.

Example flow for GET /api/recipe/recipes/:

- Router receives the request.

- Router calls list_recipes(db).

- Service fetches recipes from the database.

- Router returns the list as JSON.

Example flow for GET /recipes/5/ (HTML):

- Router receives the request.

- Router calls get_recipe(db, 5).

- Service fetches the recipe.

- Router renders recipe_detail.html with the recipe data.

This structure keeps routers lightweight and easy to understand.

### What routers should NOT contain:

- SQLAlchemy queries

- ORM session logic

- Business rules

- Data transformations

- Template definitions

- Application setup logic

### Why this structure matters:
Routers remain clean and readable because they only coordinate requests and responses. All heavy lifting is done by the services layer. This separation makes the project easier to maintain, test, and extend.