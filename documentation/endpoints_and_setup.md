# Endpoints and Setup Documentation

## API Endpoints

### 1. AI Support Response
```python
@router.post("/ai_faq_search", response_model=SupportResponse)
async def get_ai_support_response(
    request: QueryRequest,
    ai_support_manager: AISupportManager = Depends(get_ai_support_manager_dependency)
) -> SupportResponse:
    """
    Generate AI-powered support response based on user query.
    
    Args:
        request: QueryRequest containing user query and ID
        ai_support_manager: Injected AISupportManager instance
    
    Returns:
        SupportResponse containing AI-generated response and relevant documents
    """
    return await ai_support_manager.get_ai_support_response(request.query, request.user_id)
```

### 2. Personal Recommendations
```python
@router.post("/recommendations", response_model=RecommendationResponse)
async def get_personal_recommendations(
    request: QueryRequest,
    ai_support_manager: AISupportManager = Depends(get_ai_support_manager_dependency)
) -> RecommendationResponse:
    """
    Generate personalized recommendations based on user history.
    
    Args:
        request: QueryRequest containing user query and ID
        ai_support_manager: Injected AISupportManager instance
    
    Returns:
        RecommendationResponse containing personalized recommendations
    """
    return await ai_support_manager.get_personal_recommendation(request.user_id)
```

## Database Setup

### 1. PostgreSQL with pgvector
```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create FAQ documents table
CREATE TABLE faq_documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    category faq_category,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create user responses table
CREATE TABLE user_responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search
CREATE INDEX faq_documents_embedding_idx ON faq_documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 2. AsyncPG Connection Pool
```python
from asyncpg import create_pool

async def get_database_connection():
    """
    Create and return a database connection pool.
    
    Returns:
        Pool: AsyncPG connection pool
    """
    return await create_pool(
        dsn=os.getenv("DATABASE_URL"),
        min_size=5,
        max_size=20,
        command_timeout=60,
        statement_cache_size=100
    )
```

### 3. Database Migrations
```python
# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv("DATABASE_URL")
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

## Docker Setup

### 1. Dockerfile
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

### 2. Docker Compose
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

## AsyncPG Best Practices

### 1. Connection Pooling
```python
class DatabaseManager:
    def __init__(self):
        self.pool = None

    async def initialize(self):
        """Initialize the connection pool."""
        self.pool = await create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=5,
            max_size=20,
            command_timeout=60
        )

    async def get_connection(self):
        """Get a connection from the pool."""
        return await self.pool.acquire()

    async def release_connection(self, connection):
        """Release a connection back to the pool."""
        await self.pool.release(connection)
```

### 2. Transaction Management
```python
async def execute_transaction(self, query: str, params: dict):
    """
    Execute a query within a transaction.
    
    Args:
        query: SQL query to execute
        params: Query parameters
    
    Returns:
        Query result
    """
    async with self.pool.acquire() as connection:
        async with connection.transaction():
            return await connection.fetch(query, **params)
```

### 3. Error Handling
```python
async def safe_execute(self, query: str, params: dict):
    """
    Execute a query with proper error handling.
    
    Args:
        query: SQL query to execute
        params: Query parameters
    
    Returns:
        Query result
    
    Raises:
        DatabaseError: If query execution fails
    """
    try:
        return await self.execute_transaction(query, params)
    except asyncpg.PostgresError as e:
        logger.error(f"Database error: {str(e)}")
        raise DatabaseError(f"Failed to execute query: {str(e)}")
```

## Performance Optimization

### 1. Connection Pool Settings
```python
POOL_SETTINGS = {
    'min_size': 5,  # Minimum connections
    'max_size': 20,  # Maximum connections
    'command_timeout': 60,  # Query timeout
    'statement_cache_size': 100,  # Prepared statement cache
    'max_cached_statement_lifetime': 300  # Cache lifetime in seconds
}
```

### 2. Query Optimization
```python
# Use prepared statements
async def get_user_history(self, user_id: int):
    query = """
    SELECT query, created_at 
    FROM user_responses 
    WHERE user_id = $1 
    ORDER BY created_at DESC 
    LIMIT 10
    """
    return await self.pool.fetch(query, user_id)

# Use batch operations
async def save_user_responses(self, responses: List[UserResponse]):
    query = """
    INSERT INTO user_responses (user_id, query, response)
    SELECT * FROM unnest($1::int[], $2::text[], $3::text[])
    """
    user_ids = [r.user_id for r in responses]
    queries = [r.query for r in responses]
    response_texts = [r.response for r in responses]
    await self.pool.execute(query, user_ids, queries, response_texts)
```

### 3. Vector Search Optimization
```python
# Create efficient index
CREATE INDEX faq_documents_embedding_idx ON faq_documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

# Optimize similarity search
async def find_similar_documents(self, embedding: List[float], limit: int = 5):
    query = """
    SELECT content, category, 
           1 - (embedding <=> $1) as similarity
    FROM faq_documents
    WHERE 1 - (embedding <=> $1) > 0.7
    ORDER BY similarity DESC
    LIMIT $2
    """
    return await self.pool.fetch(query, embedding, limit)
```

## Monitoring and Logging

### 1. Database Metrics
```python
# Track query performance
QUERY_TIME = Histogram(
    'database_query_time_seconds',
    'Time taken to execute database queries',
    ['query_type']
)

@metrics.track_time(QUERY_TIME, {'query_type': 'user_history'})
async def get_user_history(self, user_id: int):
    # Implementation
    pass
```

### 2. Connection Pool Metrics
```python
# Track pool usage
POOL_SIZE = Gauge(
    'database_pool_size',
    'Current size of the database connection pool'
)

POOL_AVAILABLE = Gauge(
    'database_pool_available',
    'Number of available connections in the pool'
)

async def update_pool_metrics(self):
    """Update connection pool metrics."""
    POOL_SIZE.set(self.pool.get_size())
    POOL_AVAILABLE.set(self.pool.get_active_size())
```

### 3. Error Tracking
```python
# Track database errors
DB_ERRORS = Counter(
    'database_errors_total',
    'Total number of database errors',
    ['error_type']
)

async def safe_execute(self, query: str, params: dict):
    try:
        return await self.execute_transaction(query, params)
    except asyncpg.PostgresError as e:
        DB_ERRORS.labels(error_type=type(e).__name__).inc()
        raise
``` 