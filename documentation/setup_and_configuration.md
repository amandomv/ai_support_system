# Setup and Configuration

## Overview
This document explains how to set up and configure the AI Support System, including environment setup, database configuration, and service dependencies.

## Prerequisites

### System Requirements
- Python 3.9 or higher
- PostgreSQL 13+ with pgvector extension
- Docker (optional)
- OpenAI API key

### Required Tools
- Git for version control
- Python virtual environment
- PostgreSQL client
- Docker (optional)

## Installation Steps

### 1. Clone and Setup
```bash
# Clone repository
git clone https://github.com/shakers/ai-support-system.git
cd ai-support-system

# Set up Python environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file with these essential settings:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_support
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=ai_support

# OpenAI
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
```

### 3. Database Setup
Choose either Docker or manual setup:

#### Docker Setup
```bash
docker-compose up -d db
```

#### Manual Setup
1. Install PostgreSQL
2. Install pgvector extension
3. Create database and user
4. Run migrations

### 4. Initialize System
```bash
python src/scripts/init_database.py
```

## Configuration Details

### Database Configuration
- Connection pooling for performance
- Vector search optimization
- Index management
- Backup settings

### API Configuration
- Rate limiting for stability
- CORS for security
- Authentication setup
- Logging configuration

### AI Model Configuration
- Model selection and parameters
- Temperature settings
- Token limits
- Embedding configuration

### Monitoring Setup
- Prometheus metrics
- Grafana dashboards
- Alert rules
- Log aggregation

## Development Environment

### Local Development
```bash
# Start server
uvicorn src.main:app --reload

# Run tests
pytest

# Check code quality
flake8
```

### Docker Development
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Run tests
docker-compose run --rm app pytest
```

## Production Deployment

### Docker Deployment
```bash
# Build and run
docker build -t ai-support-system:prod .
docker run -d \
    --name ai-support \
    -p 8000:8000 \
    --env-file .env.prod \
    ai-support-system:prod
```

### Kubernetes Deployment
```bash
# Deploy
kubectl apply -f k8s/

# Verify
kubectl get pods
kubectl get services
```

## System Maintenance

### Health Monitoring
- API health checks
- Database connectivity
- AI service status
- System metrics

### Backup Procedures
- Database backups
- Configuration backups
- Log management
- Disaster recovery

### Performance Tuning
- Database optimization
- Cache configuration
- Load balancing
- Resource management

## Troubleshooting

### Common Issues
- Database connection problems
- API authentication issues
- AI service timeouts
- Performance bottlenecks

### Debug Procedures
- Log analysis
- Error tracking
- Performance profiling
- Network debugging

### Support Resources
- Documentation
- Issue tracker
- Community forums
- Support channels 