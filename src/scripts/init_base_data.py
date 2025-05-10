import asyncio
import json
from typing import List, Dict
from src.infrastructure.ai_generation_repository import AIGenerationRepository
from src.types.documents import FaqDocument, FaqCategory
from src.config.settings import get_settings

# Technical documentation content
TECHNICAL_DOCS = [
    {
        "title": "Event Manager System",
        "link": "/docs/technical/event-manager",
        "text": "The AI Support System uses an EventManager for background tasks. It provides a queue-based system with multiple workers for processing events asynchronously. The EventManager handles task distribution, error handling, and event processing.",
        "category": FaqCategory.TECHNICAL
    },
    {
        "title": "Parallel Document Processing",
        "link": "/docs/technical/parallel-processing",
        "text": "Document processing is handled in parallel using ProcessPoolExecutor. Documents are split into chunks and processed by multiple workers simultaneously, improving performance for large document sets.",
        "category": FaqCategory.TECHNICAL
    },
    {
        "title": "AI Training Pipeline",
        "link": "/docs/technical/ai-training",
        "text": "The AI training pipeline includes data preparation, model training, evaluation, and model saving. It uses scikit-learn for model training and evaluation, with support for custom feature extraction and model persistence.",
        "category": FaqCategory.TECHNICAL
    },
    {
        "title": "Automated Embedding Generation",
        "link": "/docs/technical/embeddings",
        "text": "Embedding generation is automated and runs in the background. The system uses OpenAI's API to generate embeddings, which are then stored in the database and cached for future use.",
        "category": FaqCategory.TECHNICAL
    },
    {
        "title": "Performance Monitoring",
        "link": "/docs/technical/monitoring",
        "text": "Performance monitoring is implemented using Prometheus metrics. The system tracks processing times, embedding generation counts, and other key performance indicators.",
        "category": FaqCategory.TECHNICAL
    },
    {
        "title": "Database Connection Pooling",
        "link": "/docs/technical/connection-pooling",
        "text": "The system uses connection pooling for database operations. It maintains a pool of database connections to improve performance and handle concurrent requests efficiently.",
        "category": FaqCategory.TECHNICAL
    },
    {
        "title": "Event-Driven Architecture",
        "link": "/docs/technical/event-driven",
        "text": "Background tasks are managed through an event-driven architecture. The system uses an event bus to publish and subscribe to events, enabling asynchronous processing of tasks.",
        "category": FaqCategory.TECHNICAL
    },
    {
        "title": "Vector Similarity Search",
        "link": "/docs/technical/vector-search",
        "text": "Vector similarity search is implemented using pgvector. The system creates efficient indexes for vector operations and uses cosine similarity for document matching.",
        "category": FaqCategory.TECHNICAL
    },
    {
        "title": "Caching Strategies",
        "link": "/docs/technical/caching",
        "text": "The system implements caching strategies using Redis. Frequently used embeddings and query results are cached to improve response times and reduce API calls.",
        "category": FaqCategory.TECHNICAL
    },
    {
        "title": "Error Handling and Logging",
        "link": "/docs/technical/error-handling",
        "text": "Error handling and logging are implemented throughout the system. Errors are caught, logged, and handled appropriately, with support for error tracking and monitoring.",
        "category": FaqCategory.TECHNICAL
    }
]

# Add technical docs to the existing faq_documents_list
faq_documents_list.extend([
    FaqDocument(
        title=doc["title"],
        link=doc["link"],
        text=doc["text"],
        category=doc["category"]
    )
    for doc in TECHNICAL_DOCS
])

async def init_base_data():
    """Initialize base data for the AI Support System."""
    settings = get_settings()
    ai_repo = AIGenerationRepository(settings)
    
    # Process all documents including technical docs
    await ai_repo.save_documents(faq_documents_list)
    
    print(f"Added {len(faq_documents_list)} documents to the database")

if __name__ == "__main__":
    asyncio.run(init_base_data()) 