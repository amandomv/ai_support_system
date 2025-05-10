# Installation Steps

## Prerequisites

### 1. System Requirements
- Python 3.11 or higher
- PostgreSQL 15 or higher
- Docker and Docker Compose
- Git

### 2. Required Extensions
- pgvector extension for PostgreSQL
- Redis (for caching)
- OpenSSL (for security)

## Installation Process

### 1. Clone Repository
```bash
git clone https://github.com/your-repo/ai_support_system.git
cd ai_support_system
```

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Create .env file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Initialize database
python src/scripts/init_db.py

# Run migrations
alembic upgrade head
```

### 4. Docker Setup
```bash
# Build and start services
docker-compose up -d

# Verify services are running
docker-compose ps
```

## Configuration

### 1. Environment Variables
```env
# Database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=ai_support
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# OpenAI
OPENAI_API_KEY=your_api_key

# Redis
REDIS_URL=redis://localhost:6379

# Application
PORT=8000
HOST=0.0.0.0
DEBUG=false
```

### 2. Database Configuration
```python
# src/config/database.py
DATABASE_CONFIG = {
    'min_connections': 5,
    'max_connections': 20,
    'command_timeout': 60,
    'statement_cache_size': 100
}
```

### 3. API Configuration
```python
# src/config/api.py
API_CONFIG = {
    'rate_limit': '100/minute',
    'timeout': 30,
    'max_retries': 3
}
```

## Verification Steps

### 1. Database Verification
```bash
# Check database connection
python src/scripts/verify_db.py

# Check pgvector extension
psql -U your_user -d ai_support -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### 2. API Verification
```bash
# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### 3. Embedding Service Verification
```bash
# Test embedding generation
python src/scripts/test_embeddings.py
```

## Troubleshooting

### 1. Common Issues
- Database connection errors
- Missing extensions
- Environment variable issues
- Port conflicts

### 2. Solutions
```bash
# Reset database
python src/scripts/reset_db.py

# Check logs
docker-compose logs -f

# Verify environment
python src/scripts/verify_env.py
```

## Security Setup

### 1. SSL Configuration
```bash
# Generate SSL certificates
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### 2. API Key Setup
```bash
# Generate API key
python src/scripts/generate_api_key.py

# Configure API key in .env
echo "API_KEY=$(python src/scripts/generate_api_key.py)" >> .env
```

## Monitoring Setup

### 1. Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai_support'
    static_configs:
      - targets: ['localhost:8000']
```

### 2. Grafana Setup
```bash
# Start Grafana
docker-compose up -d grafana

# Access Grafana
open http://localhost:3000
```

## Backup and Recovery

### 1. Database Backup
```bash
# Create backup
pg_dump -U your_user -d ai_support > backup.sql

# Schedule regular backups
crontab -e
# Add: 0 0 * * * pg_dump -U your_user -d ai_support > /backups/backup_$(date +\%Y\%m\%d).sql
```

### 2. Recovery Process
```bash
# Restore from backup
psql -U your_user -d ai_support < backup.sql
``` 