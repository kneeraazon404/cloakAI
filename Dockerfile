FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git gcc g++ libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Fawkes core library
COPY core /tmp/fawkes_core
RUN pip install --no-cache-dir /tmp/fawkes_core

# Copy backend source
COPY api ./api
COPY worker ./worker
COPY config.py .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
