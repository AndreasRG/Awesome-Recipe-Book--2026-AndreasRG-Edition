FROM python:3.12-slim

WORKDIR /app

# Copy requirements from the build context root
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code (the app/ folder)
COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
