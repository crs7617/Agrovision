# Backend Dockerfile - FastAPI
FROM python:3.12-slim

# set workdir
WORKDIR /app

# install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# copy requirements first for caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest
COPY . .

# Expose port
EXPOSE 8000

# Use environment variables for host/port if provided
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
