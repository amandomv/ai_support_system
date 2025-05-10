# System Architecture

## Overview
The AI Support System is built using a clean architecture approach, separating concerns into distinct layers and following SOLID principles. The system is designed to be modular, testable, and maintainable.

## Core Components

### 1. Application Layer
- **AISupportManager**: Central orchestrator that coordinates between different repositories and handles business logic
- **Interfaces**: Define contracts for repositories and external services
  - `AISupportInterface`: Handles user interactions and FAQ document retrieval
  - `AIGenerationInterface`: Manages AI-related operations (embeddings, responses)

### 2. Infrastructure Layer
- **Repositories**: Implement the interfaces and handle data persistence
  - `AISupportRepository`: Manages user responses and FAQ documents
  - `AIGenerationRepository`: Handles OpenAI interactions
- **Database**: PostgreSQL with vector support for embeddings
- **Metrics**: Prometheus integration for monitoring

### 3. API Layer
- FastAPI router handling HTTP requests
- Dependency injection for clean service management
- Pydantic models for request/response validation

## Design Patterns

### Repository Pattern
- Abstracts data access logic
- Provides a clean interface for data operations
- Makes testing easier through dependency injection

### Dependency Injection
- Services are injected through FastAPI's dependency system
- Makes the system more modular and testable
- Allows for easy swapping of implementations

### Factory Pattern
- Used for creating repository instances
- Centralizes object creation logic
- Makes configuration management easier

## Data Flow

1. **User Query Processing**:
   ```
   HTTP Request → Router → AISupportManager → AI Generation → Response
   ```

2. **Recommendation Generation**:
   ```
   User History → AISupportManager → AI Analysis → Personalized Recommendations
   ```

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with pgvector
- **AI**: OpenAI API (GPT-4, text-embedding-3-small)
- **Testing**: pytest
- **Monitoring**: Prometheus
- **Documentation**: Markdown

## Directory Structure

```
src/
├── application/          # Business logic
│   ├── interfaces/      # Interface definitions
│   └── ai_support_manager.py
├── infrastructure/      # External services and persistence
│   ├── ai_generation_repository.py
│   ├── ai_support_repository.py
│   └── prometheus_metrics.py
├── types/              # Data models
├── dependencies/       # Dependency injection
└── ai_response_router.py
```

## Key Features

1. **Semantic Search**
   - Vector embeddings for FAQ documents
   - Similarity-based document retrieval

2. **Personalized Recommendations**
   - User history analysis
   - Pattern recognition
   - Topic-based suggestions

3. **Monitoring**
   - Response time tracking
   - Embedding generation metrics
   - Document search performance

## Security Considerations

1. **API Key Management**
   - Environment-based configuration
   - Secure storage of OpenAI keys

2. **Input Validation**
   - Pydantic models for request validation
   - Type checking and sanitization

3. **Error Handling**
   - Structured error responses
   - Proper logging and monitoring 