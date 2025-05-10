# Testing Documentation

## Overview
The AI Support System uses pytest as its testing framework, with a focus on unit testing, integration testing, and mocking external dependencies. The testing strategy follows the Arrange-Act-Assert pattern and emphasizes test isolation and maintainability.

## Test Structure

### 1. Unit Tests
Located in `tests/unit/`, these tests focus on individual components:
- Repository implementations
- Manager logic
- Utility functions

### 2. Integration Tests
Located in `tests/integration/`, these tests verify:
- Database interactions
- API endpoints
- Component integration

### 3. Mock Tests
Located in `tests/mocks/`, these tests:
- Mock external services (OpenAI)
- Simulate database responses
- Test error scenarios

## Test Categories

### Repository Tests
```python
# Example: AI Support Repository Test
async def test_get_user_query_history():
    # Arrange
    repository = AISupportRepository()
    user_id = 1
    
    # Act
    history = await repository.get_user_query_history(user_id)
    
    # Assert
    assert isinstance(history, UserQueryHistory)
    assert len(history.queries) > 0
```

### Manager Tests
```python
# Example: AI Support Manager Test
async def test_get_personal_recommendation():
    # Arrange
    manager = AISupportManager()
    user_id = 1
    
    # Act
    recommendations = await manager.get_personal_recommendation(user_id)
    
    # Assert
    assert isinstance(recommendations, RecommendationResponse)
    assert len(recommendations.recommendations) > 0
```

### API Tests
```python
# Example: Router Test
async def test_get_personal_recommendations_endpoint():
    # Arrange
    client = TestClient(app)
    request_data = {"query": "test", "user_id": 1}
    
    # Act
    response = client.post("/recommendations", json=request_data)
    
    # Assert
    assert response.status_code == 200
    assert "recommendations" in response.json()
```

## Mocking Strategy

### 1. Database Mocks
```python
@pytest.fixture
def mock_db_connection():
    return AsyncMock()
```

### 2. OpenAI Mocks
```python
@pytest.fixture
def mock_openai_client():
    client = AsyncMock()
    client.embeddings.create.return_value = {
        "data": [{"embedding": [0.1, 0.2, 0.3]}]
    }
    return client
```

### 3. Repository Mocks
```python
@pytest.fixture
def mock_ai_support_repository():
    repository = AsyncMock()
    repository.get_user_query_history.return_value = UserQueryHistory(
        queries=["test query"]
    )
    return repository
```

## Test Configuration

### 1. Environment Setup
```python
# conftest.py
@pytest.fixture(autouse=True)
def setup_test_env():
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
```

### 2. Database Setup
```python
@pytest.fixture
async def test_db():
    # Create test database
    async with AsyncClient() as client:
        await client.execute("CREATE DATABASE test_db")
    yield
    # Cleanup
    async with AsyncClient() as client:
        await client.execute("DROP DATABASE test_db")
```

## Running Tests

### Command Line
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_ai_support_manager.py

# Run with coverage
pytest --cov=src tests/
```

### Test Categories
```bash
# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run mock tests only
pytest tests/mocks/
```

## Best Practices

1. **Test Isolation**
   - Each test should be independent
   - Use fixtures for setup and teardown
   - Clean up resources after tests

2. **Naming Conventions**
   - Test files: `test_*.py`
   - Test functions: `test_*`
   - Clear, descriptive names

3. **Assertions**
   - Use specific assertions
   - Test both success and failure cases
   - Verify edge cases

4. **Code Coverage**
   - Aim for high coverage
   - Focus on critical paths
   - Document uncovered code

## Common Issues and Solutions

1. **Async Testing**
   - Use `pytest-asyncio`
   - Properly handle async fixtures
   - Use `async def` for test functions

2. **Database Testing**
   - Use test database
   - Clean up after tests
   - Mock when appropriate

3. **External Services**
   - Mock API calls
   - Simulate responses
   - Test error handling 