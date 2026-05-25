FROM python:3.12-slim

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code
COPY app/ .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
