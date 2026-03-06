# Understanding the Services Layer

## Overview:
The services layer contains all business logic and database operations. Services interact directly with SQLAlchemy models and the async database session. Routers call services, but services never import routers. This creates a clean separation between the API layer and the business logic layer.

### Service Groups:

1 - Recipe Services

- Fetch all recipes with tags and ingredients.

- Fetch a single recipe by ID.

- Create new recipes and attach tags and ingredients.

- Handle ORM operations such as commit, refresh, and relationship loading.

2 - User Services

- Create new users.

- Authenticate users by email and password.

- Handle all user-related database queries.

### How endpoints interact with the services layer:

Services contain the logic that endpoints depend on. When a router receives a request, it never performs database operations directly. Instead, it calls a service function. This ensures that all business logic is centralized and reusable.

*NOTE: All endpoints use the base URL "http://localhost:5000".*

Example: GET /api/recipe/recipes/

- Router calls list_recipes(db)

- Service executes a SQLAlchemy query

- Service returns ORM objects

- Router returns them as JSON

Example: POST /api/recipe/recipes/

- Router validates the incoming RecipeCreate schema

- Router calls create_recipe(db, data)

- Service creates the Recipe ORM object

- Service attaches tags and ingredients

- Service commits the transaction

- Router returns the new recipe ID

Example: user authentication

- Router receives email and password

- Router calls authenticate_user(db, email, password)

- Service checks the database

- Service returns the user or None

- Router returns a token or an error

This separation ensures that:

- Routers handle HTTP

- Services handle logic

- Models handle data

- app.py handles application setup

This makes the project maintainable, testable, and scalable.

### What services should NOT contain:

- FastAPI imports

- HTTPException

- Request or Response objects

- Template rendering

- Routing logic

- Application setup code

### Why this structure matters:
By isolating business logic in services, the project becomes modular and testable. Services can be reused across routers, background tasks, or even future CLI tools. This architecture also prevents duplication and keeps routers lightweight.