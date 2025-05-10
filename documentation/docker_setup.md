# Docker Setup Documentation

## Overview
The AI Support System is containerized using Docker and Docker Compose for easy deployment and scalability. The setup includes the main application, PostgreSQL database with pgvector, and Prometheus for monitoring.

## Dockerfile

### 1. Base Configuration
```dockerfile
# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run migrations and start application
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
```

### 2. Multi-stage Build (Optional)
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
```

## Docker Compose

### 1. Basic Setup
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/ai_support
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - prometheus

  db:
    image: ankane/pgvector:latest
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=ai_support
    volumes:
      - postgres_data:/var/lib/postgresql/data

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

volumes:
  postgres_data:
```

### 2. Development Setup
```yaml
version: '3.8'

services:
  app:
    build: 
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/ai_support
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - db

  db:
    image: ankane/pgvector:latest
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=ai_support
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Environment Variables

### 1. Application Variables
```env
# Database
DATABASE_URL=postgresql://user:password@db:5432/ai_support

# OpenAI
OPENAI_API_KEY=your-api-key

# Application
PORT=8000
HOST=0.0.0.0
DEBUG=false
```

### 2. Database Variables
```env
# PostgreSQL
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=ai_support
POSTGRES_PORT=5432
```

## Deployment

### 1. Local Development
```bash
# Start services
docker-compose up -d

# Run migrations
docker-compose exec app alembic upgrade head

# View logs
docker-compose logs -f app
```

### 2. Production
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale app=3
```

## Health Checks

### 1. Application Health
```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 2. Database Health
```yaml
services:
  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d ai_support"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## Monitoring

### 1. Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai_support'
    static_configs:
      - targets: ['app:8000']
```

### 2. Grafana Dashboard
```yaml
services:
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  grafana_data:
```

## Best Practices

1. **Security**
   - Use secrets for sensitive data
   - Implement health checks
   - Use non-root users

2. **Performance**
   - Use multi-stage builds
   - Optimize layer caching
   - Configure resource limits

3. **Maintenance**
   - Regular base image updates
   - Clean up unused resources
   - Monitor container health

4. **Development**
   - Use volume mounts for code
   - Enable hot reloading
   - Configure debugging 