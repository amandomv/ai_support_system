# Database Setup Documentation

## Overview
The AI Support System uses PostgreSQL with pgvector extension for storing and querying vector embeddings. The database is designed to handle FAQ documents, user responses, and vector similarity searches efficiently.

## Database Schema

### 1. FAQ Documents Table
```sql
-- Create FAQ category enum
CREATE TYPE faq_category AS ENUM (
    'general',
    'technical',
    'billing',
    'account'
);

-- Create FAQ documents table
CREATE TABLE faq_documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    category faq_category,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search
CREATE INDEX faq_documents_embedding_idx ON faq_documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 2. User Responses Table
```sql
-- Create user responses table
CREATE TABLE user_responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for user queries
CREATE INDEX user_responses_user_id_idx ON user_responses(user_id);
CREATE INDEX user_responses_created_at_idx ON user_responses(created_at);
```

## Connection Management

### 1. Connection Pool
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

### 2. Pool Settings
```python
POOL_SETTINGS = {
    'min_size': 5,  # Minimum connections
    'max_size': 20,  # Maximum connections
    'command_timeout': 60,  # Query timeout
    'statement_cache_size': 100,  # Prepared statement cache
    'max_cached_statement_lifetime': 300  # Cache lifetime in seconds
}
```

## Database Operations

### 1. Vector Similarity Search
```python
async def find_similar_documents(self, embedding: List[float], limit: int = 5):
    """
    Find similar documents using vector similarity search.
    
    Args:
        embedding: Document embedding vector
        limit: Maximum number of results
    
    Returns:
        List of similar documents
    """
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

### 2. User History Retrieval
```python
async def get_user_history(self, user_id: int, limit: int = 10):
    """
    Get user query history.
    
    Args:
        user_id: User identifier
        limit: Maximum number of queries
    
    Returns:
        List of user queries
    """
    query = """
    SELECT query, created_at 
    FROM user_responses 
    WHERE user_id = $1 
    ORDER BY created_at DESC 
    LIMIT $2
    """
    return await self.pool.fetch(query, user_id, limit)
```

## Migrations

### 1. Migration Setup
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

### 2. Migration Commands
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Performance Optimization

### 1. Index Optimization
```sql
-- Create efficient indexes
CREATE INDEX faq_documents_category_idx ON faq_documents(category);
CREATE INDEX user_responses_user_id_created_at_idx ON user_responses(user_id, created_at);
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

## Monitoring

### 1. Query Performance
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

## Best Practices

1. **Connection Management**
   - Use connection pooling
   - Properly close connections
   - Handle connection errors

2. **Query Optimization**
   - Use prepared statements
   - Create appropriate indexes
   - Optimize vector searches

3. **Error Handling**
   - Handle database errors
   - Implement retry logic
   - Log errors properly

4. **Monitoring**
   - Track query performance
   - Monitor connection pool
   - Set up alerts 