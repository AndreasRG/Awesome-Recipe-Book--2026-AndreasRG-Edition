# Awesome Recipe Book — 2026 AndreasRG Edition

## Overview
Awesome Recipe Book is a modern, multi-layered web application that demonstrates a production-ready architecture for a recipe management service. This edition is refactored from the original Cookbook project to use:

- **FastAPI** for high-performance request handling
- **Async SQLAlchemy** for non-blocking database access
- **Jinja2** for server-side HTML rendering
- **Docker** for containerized deployment
- **GitHub Actions** for CI/CD automation

The repository is designed to support a 2-VM deployment model with separate application and proxy layers, including a blue-green reverse-proxy strategy for zero-downtime updates.

## Architecture Summary

### Logical separation
- **App VM**: Hosts the FastAPI application, database, and application-level services
- **Proxy VM**: Hosts the reverse proxy, monitoring stack, and external ingress

### Deployment pattern
- **App layer**: 3 application instances behind an internal reverse proxy
- **Proxy layer**: Blue/Green reverse-proxy deployment on HTTP port 80
- **Database VM**: Dedicated database host reachable via the `DATABASE_URL` defined in `app/database.py`
- **Monitoring**: Prometheus and Grafana are colocated on the proxy VM for centralized observability

### Key capabilities
- Zero-downtime proxy deployments via blue-green switching
- Health-checked application rollout
- Authentication-aware front-end flow for login and recipe creation
- Dedicated database VM accessible by application instances
- Modular separation of routers, services, and database models

## Repository Structure

- `app/`: FastAPI application source code
  - `app.py`: application bootstrap and router registration
  - `database.py`: async SQLAlchemy engine, session factory, and initialization
  - `models.py`: ORM model definitions
  - `routers/`: HTTP route definitions for pages, recipes, and users
  - `services/`: business logic and persistence operations
  - `templates/`: Jinja2 HTML views
  - `static/`: front-end assets

- `reverse-proxy/`: Nginx proxy configuration
- `monitoring/`: Prometheus monitoring definitions
- `scripts/`: deployment and orchestration helpers
- `.github/workflows/`: CI/CD workflows

## Deployment Overview

### App VM
- `docker-compose.app.yml` orchestrates the application containers and node exporter
- `scripts/rolling_update.sh` performs rolling updates with health checks
- Application containers expose internal port `5000`

### Proxy VM
- `docker-compose.proxy-blue.yml` and `docker-compose.proxy-green.yml` support blue-green deployment
- `scripts/blue_green_proxy_deploy.sh` handles proxy activation and switch-over
- External ingress is served on **HTTP port 80 only**

### GitHub Actions
- Build and publish Docker images to GHCR
- Deploy application VM via SSH and rolling update script
- Deploy proxy VM via SSH and blue-green proxy script

## Running Locally

### Python development

```bash
git clone https://github.com/AndreasRG/Awesome-Recipe-Book--2026-AndreasRG-Edition.git
cd Awesome-Recipe-Book--2026-AndreasRG-Edition
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in your browser.

### Docker

```bash
docker build -t awesome-recipe-book .
docker run --rm -p 5000:5000 awesome-recipe-book
```

Open `http://localhost:5000` in your browser.

## Notes

- The application is intended as a learning and architectural demonstration.
- Authentication is implemented via cookie-based sessions and guards recipe creation.
- Proxy deployment is configured for HTTP only on port 80.
- The database uses SQLite with SQLAlchemy for a simplified local development experience.

## Further Reading

- `app/README_app.md`: application architecture and bootstrap details
- `app/routers/README_routers.md`: router layer responsibilities
- `app/services/README_services.md`: services layer responsibilities

## License

This project is published under the **MIT License**.
