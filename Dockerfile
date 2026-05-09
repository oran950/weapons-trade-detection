# Root Dockerfile for hosts that only look at repo root (e.g. Render with root = .).
# Equivalent to building with context backend/ and backend/Dockerfile.
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 9000

CMD ["python", "-m", "uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "9000"]
