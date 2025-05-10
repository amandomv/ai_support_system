# API Endpoints Documentation

## Overview
The AI Support System provides two main endpoints for handling user queries and generating recommendations. Both endpoints use FastAPI's dependency injection system and follow RESTful principles.

## Endpoints

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

#### Request Model
```python
class QueryRequest(BaseModel):
    query: str
    user_id: int
```

#### Response Model
```python
class SupportResponse(BaseModel):
    response: str
    relevant_documents: List[FaqDocument]
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

#### Request Model
```python
class QueryRequest(BaseModel):
    query: str
    user_id: int
```

#### Response Model
```python
class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
```

## Error Handling

### 1. Validation Errors
```python
class ValidationError(BaseModel):
    detail: str
    status_code: int = 400
```

### 2. Database Errors
```python
class DatabaseError(BaseModel):
    detail: str
    status_code: int = 500
```

### 3. OpenAI API Errors
```python
class OpenAIError(BaseModel):
    detail: str
    status_code: int = 503
```

## Response Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: External service unavailable

## Rate Limiting

```python
@router.post("/ai_faq_search")
@limiter.limit("5/minute")
async def get_ai_support_response():
    # Implementation
    pass
```

## Security

### 1. API Key Authentication
```python
@router.post("/recommendations")
async def get_personal_recommendations(
    api_key: str = Header(..., alias="X-API-Key")
):
    # Implementation
    pass
```

### 2. Input Validation
```python
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    user_id: int = Field(..., gt=0)
```

## Monitoring

### 1. Response Time
```python
@metrics.track_time(RESPONSE_TIME, {'endpoint': 'support'})
async def get_ai_support_response():
    # Implementation
    pass
```

### 2. Request Count
```python
@metrics.track_usage(REQUEST_COUNT, {'endpoint': 'support'})
async def get_ai_support_response():
    # Implementation
    pass
```

## Best Practices

1. **Input Validation**
   - Use Pydantic models
   - Validate all inputs
   - Sanitize user data

2. **Error Handling**
   - Use appropriate status codes
   - Provide meaningful error messages
   - Log errors properly

3. **Performance**
   - Use async/await
   - Implement caching
   - Monitor response times

4. **Security**
   - Validate API keys
   - Rate limit requests
   - Sanitize inputs 