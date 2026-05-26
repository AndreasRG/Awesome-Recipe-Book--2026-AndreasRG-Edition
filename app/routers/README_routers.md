# Router Layer Documentation

## Purpose
The router layer exposes the public HTTP interface for the application. It is the transport boundary between clients and the application domain.

## Responsibilities
Routers are responsible for:

- Accepting HTTP requests
- Validating request payloads with Pydantic schemas
- Binding dependencies such as database sessions and authenticated user context
- Delegating business operations to the services layer
- Returning JSON responses or rendering HTML templates

Routers should remain lightweight and declarative. They do not implement business rules or perform direct persistence operations.

## Router Modules

### `pages.py`
- Handles HTML page rendering for the public website
- Exposes routes such as home, recipe detail, and recipe creation
- Injects authenticated user state into templates
- Uses services to retrieve recipe content and user context

### `recipes.py`
- Exposes REST API endpoints for recipe data
- Supports list, retrieve, and create operations
- Uses Pydantic request models to validate payloads
- Enforces authentication for recipe creation

### `users.py`
- Manages authentication and session routes
- Supports login, signup, logout, and token creation
- Delegates user persistence and credential validation to services

## Request Flow

1. Client sends an HTTP request.
2. FastAPI routes the request to the appropriate router.
3. The router validates input and resolves dependencies.
4. The router calls a service function.
5. The service returns the result.
6. The router returns a response or renders a template.

## Why this separation matters

This architecture separates transport concerns from domain logic, which enables:

- easier testing of business logic in services
- clear HTTP contract management in routers
- reduced coupling between routing and persistence
- better scalability and maintainability for the codebase

## What routers should not contain

- SQLAlchemy ORM queries
- Direct session management
- Domain rule enforcement
- Template structure or layout logic
- Application startup or configuration code
