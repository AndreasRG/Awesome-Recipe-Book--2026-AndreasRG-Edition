# Understanding app.py

## Overview:
The app.py file is the central entry point of the application. It creates the FastAPI instance, loads configuration, mounts static files, initializes templates, includes all routers, and runs database initialization on startup. This file does not contain business logic or routing logic. Instead, it acts as the “application assembler,” wiring together the different parts of the project.

### Key Responsibilities:

- Create the FastAPI application instance.

- Mount the /static directory so CSS, JS, and images can be served.

- Initialize Jinja2 templates for HTML rendering.

- Include all routers (pages, recipes, users).

- Run database initialization when the server starts.

- Provide a simple API overview endpoint.

- Start the application when executed with “python app.py”.

### How endpoints work in the application:

The app.py file does not define any endpoints itself (except the optional /api overview). Instead, it loads all endpoints from the routers. When the application starts, app.py includes the routers, and FastAPI automatically registers every route defined inside them. This means app.py acts as the central hub that exposes all API and HTML endpoints to the outside world.

When a request comes in, FastAPI checks which router the path belongs to. All endpoints use the base URL "http://localhost:5000". For example:

- A request to “/api/recipe/recipes/” is routed to the recipes router.

- A request to “/api/user/create/” is routed to the users router.

- A request to “/recipes/5/” is routed to the pages router for HTML rendering.

app.py itself does not process the request. It simply ensures that all routers are active and that the database is initialized before any endpoint is used.

This separation keeps app.py clean and ensures that all endpoint logic lives in the routers and services.

### What app.py should NOT contain:

- Database models

- Business logic

- ORM queries

- HTML templates

- API route definitions

- Authentication logic

- Service functions

### Why this structure matters:
Keeping app.py small and focused ensures the project remains modular, readable, and scalable. All real functionality is delegated to routers and services, while app.py simply ties everything together.