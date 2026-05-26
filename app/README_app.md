# Application Layer Overview

## Purpose
The `app/` module contains the application service and runtime assembly for Awesome Recipe Book. It is responsible for configuring FastAPI, preparing template rendering, wiring routers, and establishing database initialization before accepting requests.

## Core Responsibilities

- Instantiate the FastAPI application.
- Mount static assets under `/static`.
- Set up Jinja2 template rendering for server-side HTML pages.
- Register router modules for pages, recipes, and user functionality.
- Initialize the database schema and seed data on startup.
- Expose the entrypoint for production execution using Uvicorn.

## Architecture

The application layer is intentionally thin and compositional:

- `app.app` acts as the application bootstrap and dependency wiring point.
- `app.routers` contains route definitions and HTTP endpoint handling.
- `app.services` contains business logic, persistence orchestration, and database transactions.
- `app.models` defines the domain model and relational mapping.
- `app.database` provides the async engine, session factory, and migration-ready initialization logic.

This layering follows standard enterprise architecture principles:
- **Presentation layer**: Request handling and template rendering
- **Application layer**: Service orchestration and router coordination
- **Persistence layer**: Database sessions, SQLAlchemy models, and transactional behavior

## Runtime Behavior

On process startup, the application performs the following sequence:

1. Create FastAPI instance.
2. Mount the `/static` folder.
3. Initialize Jinja2 templates.
4. Include routers from `app.routers`.
5. Run database initialization and seeding.
6. Start the server with `uvicorn app.app:app`.

## Production Deployment

The root `Dockerfile` packages `app/` into a container image with:
- Python 3.12
- Dependencies installed from `app/requirements.txt`
- `PYTHONPATH=/app`
- Command: `uvicorn app.app:app --host 0.0.0.0 --port 5000`

## Database VM

The application connects to a dedicated database VM via the `DATABASE_URL` environment variable in `app/database.py`.
The default connection string is:

`postgresql+asyncpg://recipe_user:admin123@27.0.0.6:5432/recipe_db`

This means the app can be configured to use an external database host while keeping the database connection logic centralized in `app/database.py`.

## Why this organization matters

Keeping `app.app` focused on application assembly ensures:
- Clean separation of concerns
- Easier onboarding for developers
- Better testability for business logic
- Reduced coupling between HTTP routing and persistence logic

For detailed component responsibilities, see:
- `app/routers/README_routers.md`
- `app/services/README_services.md`
