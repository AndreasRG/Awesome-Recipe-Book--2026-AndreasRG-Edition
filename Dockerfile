FROM python:3.12-slim

# Set working directory
WORKDIR /

# Install curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy the entire app directory to /app (preserves structure)
COPY app /app

# Install dependencies from app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Add /app to Python path so imports like 'from app.database import' work
ENV PYTHONPATH=/app:$PYTHONPATH

# Run uvicorn from root so it can find the app module
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5000"]
