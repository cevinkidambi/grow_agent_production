# ==== Backend Dockerfile: Grow Agent API ====
FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps (use backend/requirements.txt)
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Ensure Python can import "backend"
ENV PYTHONPATH=/app

# FastAPI/uvicorn port
EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 backend.main:app
