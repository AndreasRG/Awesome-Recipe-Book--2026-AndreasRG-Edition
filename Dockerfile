FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Use env file at runtime (we'll mount it on the VM)
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5000"]