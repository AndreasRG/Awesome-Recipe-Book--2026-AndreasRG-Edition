# Services Layer Documentation

## Purpose
The services layer encapsulates business rules, persistence operations, and transactional workflow for the application. It is the domain logic core of Awesome Recipe Book.

## Responsibilities
Services are responsible for:

- Interacting with SQLAlchemy models and async database sessions
- Orchestrating create/read/update/delete operations
- Applying business rules for recipes and users
- Managing transactions, commits, and object refresh cycles
- Returning domain objects to the router layer

Services should never depend on HTTP concepts, request objects, or template rendering.

## Service Groups

### Recipe Services
- `list_recipes`: retrieve recipe listings with tags and ingredient metadata
- `get_recipe`: fetch a single recipe by ID with related entities
- `create_recipe`: persist a new recipe and associate tags/ingredients
- Ensures that recipe creation is consistent and that relationships are configured correctly

### User Services
- `create_user`: persist a new user record
- `authenticate_user`: validate credentials against stored user data
- `login_user`: orchestrate authentication workflow
- `register_user_from_form`: convert user input into domain payloads

## Interaction Pattern

The router layer delegates application workflows to services. A typical interaction looks like:

1. Router validates request data with Pydantic.
2. Router calls a service function with the database session.
3. Service executes ORM operations and business rules.
4. Service returns domain entities or error state.
5. Router serializes the result to JSON or templates.

## Why this separation matters

Centralizing business logic in services enables:

- better unit testing for domain rules
- reuse of logic across multiple route handlers or future interfaces
- easier migration to alternative persistence backends
- cleaner code organization and lower coupling

## What services should not include

- FastAPI routing decorators
- HTTP request or response objects
- Template rendering logic
- Direct access to request/session middleware
- Application startup configuration

## Architectural rationale

This design adheres to standard layered architecture principles:

- **Presentation**: routers manage HTTP and templates
- **Application / Domain**: services execute business behavior
- **Persistence**: models and database sessions support data access

By keeping these layers distinct, the project remains maintainable and scalable as new functionality is added.