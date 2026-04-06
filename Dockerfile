# ── Aurum Tempus — Dockerfile ──────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Initialise DB (creates tables + seeds products)
RUN python init_db.py

# Expose FastAPI port
EXPOSE 8000

# Default: run FastAPI backend
# Override with `docker-compose up` for multi-service
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
