# AI Support System

AI-based support system that uses embeddings and similarity search to provide accurate responses based on FAQ documents.

## Features

- Embedding generation using OpenAI
- Document similarity search using pgvector
- REST API with FastAPI
- Performance metrics with Prometheus
- PostgreSQL database with pgvector
- Automatic documentation with Swagger/ReDoc

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- PostgreSQL 16+ with pgvector
- Prometheus (for metrics)

## Configuration

### 1. Environment Variables

Copy the `.env.example` file to `.env` and configure the variables:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- `POSTGRES_*`: Database configuration
- `OPENAI_API_KEY`: Your OpenAI API key
- `INIT_BASE_DATA`: `true` to initialize sample data
- `APP_PORT`: Application port (default: 8000)

## Initialization Steps

### Step 1: Start Database and Initial Data

1. Start PostgreSQL with pgvector and initial data:
```bash
docker-compose up db
```

This step:
- Starts PostgreSQL with pgvector
- Runs `init_db.py` to create tables
- Initializes base data if `INIT_BASE_DATA=true`

The database will be available at:
- Host: localhost
- Port: 5432
- User: postgres
- Password: postgres
- Database: ai_support_system

### Step 2: Start the Application

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Prometheus (in a separate terminal):
```bash
prometheus --config.file=prometheus.yml
```

4. Start the application:
```bash
python main.py
```

The application will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Metrics: http://localhost:8000/metrics
- Prometheus UI: http://localhost:9090

## Project Structure

```
.
├── src/
│   ├── application/          # Business logic
│   ├── infrastructure/       # Technical implementations
│   ├── config/              # Configuration
│   ├── database/            # Models and migrations
│   └── types/               # Types and models
├── base_data/               # Sample data
├── docker-compose.yml       # Docker configuration (database)
├── Dockerfile              # Image configuration
├── requirements.txt        # Dependencies
└── prometheus.yml         # Prometheus configuration
```

## Metrics

The system exposes metrics at `/metrics` including:

- `ai_support_response_time_seconds`: Response time
- `ai_support_responses_total`: Response counter
- `ai_embedding_generation_time_seconds`: Embedding generation time
- `ai_document_search_time_seconds`: Document search time

Access metrics at:
- Raw metrics: http://localhost:8000/metrics
- Prometheus UI: http://localhost:9090

## API Endpoints

### POST /api/query
Generates a support response based on a query.

```json
{
  "query": "How can I reset my password?",
  "user_id": 1
}
```

Response:
```json
{
  "response": "To reset your password...",
  "docs_used": [
    {
      "title": "Password Reset",
      "link": "https://example.com/reset-password"
    }
  ]
}
```

## Development

### Tests
```bash
pytest
```

### Linting
```bash
ruff check .
```

### Formatting
```bash
ruff format .
```
