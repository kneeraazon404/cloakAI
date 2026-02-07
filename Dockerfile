FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Fawkes Core Lib and Install
# We assume the context is 'backend' folder? No, usually context is root to catch shared libs.
# If we move Dockerfile to backend/, we usually build from root: `docker build -f backend/Dockerfile .`
# So COPY paths depend on context.
# Let's assume context is project root.

COPY backend/core /tmp/fawkes_lib
RUN pip install --no-cache-dir /tmp/fawkes_lib

# Copy Backend Code
COPY backend /app/backend

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Default command
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
