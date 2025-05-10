# Database Automation and Future Architecture

## Database Installation Automation

### 1. Initialization Script
```python
# src/scripts/init_db.py
import asyncio
import asyncpg
from src.config.settings import get_settings

async def init_database():
    """Initialize database with required extensions and tables."""
    settings = get_settings()
    
    # Connect to default database
    conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database='postgres'
    )
    
    try:
        # Create database if not exists
        await conn.execute(f'''
            SELECT 'CREATE DATABASE {settings.POSTGRES_DB}'
            WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{settings.POSTGRES_DB}')
        ''')
        
        # Connect to new database
        await conn.close()
        conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB
        )
        
        # Create extensions
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
        
        # Create tables
        await conn.execute('''
            CREATE TYPE faq_category AS ENUM (
                'general',
                'technical',
                'billing',
                'account'
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS faq_documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector(1536),
                category faq_category,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS faq_documents_embedding_idx 
            ON faq_documents USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        ''')
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_database())
```

### 2. Docker Entrypoint Script
```bash
#!/bin/bash
# docker-entrypoint.sh

# Wait for database to be ready
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER
do
  echo "Waiting for database..."
  sleep 2
done

# Run database initialization
python src/scripts/init_db.py

# Run migrations
alembic upgrade head

# Start application
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Document Embedding Processing

### 1. Batch Processing Service
```python
# src/services/embedding_processor.py
from typing import List
import asyncio
from openai import AsyncOpenAI
from src.types.documents import FaqDocument
from src.infrastructure.ai_generation_repository import AIGenerationRepository

class EmbeddingProcessor:
    def __init__(self, ai_repo: AIGenerationRepository):
        self.ai_repo = ai_repo
        self.client = AsyncOpenAI()
        self.batch_size = 100
        
    async def process_documents(self, documents: List[FaqDocument]):
        """Process documents in batches to generate embeddings."""
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            await self._process_batch(batch)
            
    async def _process_batch(self, documents: List[FaqDocument]):
        """Process a batch of documents."""
        # Generate embeddings
        embeddings = await self._generate_embeddings([doc.content for doc in documents])
        
        # Update documents with embeddings
        for doc, embedding in zip(documents, embeddings):
            doc.embedding = embedding
            
        # Save to database
        await self.ai_repo.save_documents(documents)
        
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [data.embedding for data in response.data]
```

### 2. Scheduled Processing
```python
# src/tasks/embedding_tasks.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.services.embedding_processor import EmbeddingProcessor

async def schedule_embedding_processing():
    """Schedule periodic embedding processing."""
    scheduler = AsyncIOScheduler()
    
    # Process new documents every hour
    scheduler.add_job(
        process_new_documents,
        'interval',
        hours=1,
        id='process_new_documents'
    )
    
    # Update existing embeddings weekly
    scheduler.add_job(
        update_existing_embeddings,
        'cron',
        day_of_week='sun',
        hour=2,
        id='update_existing_embeddings'
    )
    
    scheduler.start()
```

## Future Architecture Improvements

### 1. Microservices Architecture
```yaml
# docker-compose.microservices.yml
version: '3.8'

services:
  api_gateway:
    build: ./services/gateway
    ports:
      - "8000:8000"
    depends_on:
      - embedding_service
      - recommendation_service
      - user_service

  embedding_service:
    build: ./services/embedding
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - embedding_data:/data

  recommendation_service:
    build: ./services/recommendation
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db

  user_service:
    build: ./services/user
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db

  db:
    image: ankane/pgvector:latest
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  embedding_data:
```

### 2. Caching Layer
```python
# src/infrastructure/cache.py
from redis import asyncio as aioredis
from src.config.settings import get_settings

class CacheManager:
    def __init__(self):
        self.redis = aioredis.from_url(get_settings().REDIS_URL)
        
    async def get_cached_embedding(self, content: str) -> List[float]:
        """Get cached embedding for content."""
        key = f"embedding:{hash(content)}"
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None
        
    async def cache_embedding(self, content: str, embedding: List[float]):
        """Cache embedding for content."""
        key = f"embedding:{hash(content)}"
        await self.redis.set(key, json.dumps(embedding), ex=86400)  # 24h TTL
```

### 3. Event-Driven Architecture
```python
# src/events/event_bus.py
from typing import Callable, Dict, List
import asyncio

class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        
    async def publish(self, event_type: str, data: dict):
        """Publish event to all handlers."""
        if event_type in self._handlers:
            await asyncio.gather(
                *[handler(data) for handler in self._handlers[event_type]]
            )
            
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe handler to event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
```

### 4. Monitoring and Observability
```python
# src/monitoring/observability.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_observability():
    """Setup OpenTelemetry tracing."""
    trace.set_tracer_provider(TracerProvider())
    
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
```

## Next Steps

1. **Immediate Actions**
   - Implement database initialization script
   - Set up document embedding processing
   - Add basic monitoring

2. **Short-term Improvements**
   - Implement caching layer
   - Add event-driven architecture
   - Enhance monitoring

3. **Long-term Goals**
   - Migrate to microservices
   - Implement advanced observability
   - Add machine learning pipeline

4. **Performance Optimization**
   - Optimize embedding generation
   - Implement batch processing
   - Add caching strategies

5. **Security Enhancements**
   - Add rate limiting
   - Implement API key rotation
   - Enhance data encryption 