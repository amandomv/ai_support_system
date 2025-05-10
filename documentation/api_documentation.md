# API Documentation

## Overview
The AI Support System provides a RESTful API for interacting with our AI support features. This document explains how to use the API effectively.

## Base URL and Authentication
All API requests should be made to:
```
https://api.shakers.com/v1
```

Authentication is required for all endpoints using JWT tokens in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Core Endpoints

### AI FAQ Search
Search for answers to user questions using our AI system.

**Endpoint:** `POST /ai_system/ai_faq_search`

**Purpose:**
- Find relevant answers to user questions
- Provide context-aware responses
- Include relevant documentation links
- Support both technical and general queries

**Request:**
```json
{
    "query": "How do I set up the database?",
    "user_id": 123,
    "i_am_a_developer": true
}
```

**Response:**
```json
{
    "response": "To set up the database...",
    "docs_used": [
        {
            "title": "Database Setup Guide",
            "link": "/docs/database-setup"
        }
    ]
}
```

### Personal Recommendations
Get personalized recommendations based on user history.

**Endpoint:** `GET /ai_system/recommendations/{user_id}`

**Purpose:**
- Provide personalized content suggestions
- Improve user experience
- Guide users to relevant resources
- Track user preferences

## Error Handling

### Response Format
All error responses follow this structure:
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {}
    }
}
```

### Common Error Codes
- `400`: Invalid request parameters
- `401`: Authentication required
- `403`: Insufficient permissions
- `404`: Resource not found
- `429`: Too many requests
- `500`: Internal server error

## Rate Limiting
To ensure system stability:
- 100 requests per minute per API key
- Rate limit information in response headers
- Exponential backoff recommended
- Contact support for higher limits

## Best Practices

### Making Requests
- Use HTTPS for all requests
- Include proper authentication
- Handle rate limiting gracefully
- Implement retry logic

### Error Handling
- Check for error responses
- Implement exponential backoff
- Log error details
- Contact support for persistent issues

### Performance
- Cache responses when appropriate
- Use compression for large requests
- Implement request batching
- Monitor response times

## SDK Examples

### Python
```python
import requests

def search_faq(query: str, user_id: int, is_developer: bool = False):
    response = requests.post(
        "https://api.shakers.com/v1/ai_system/ai_faq_search",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "query": query,
            "user_id": user_id,
            "i_am_a_developer": is_developer
        }
    )
    return response.json()
```

### JavaScript
```javascript
async function searchFaq(query, userId, isDeveloper = false) {
    const response = await fetch(
        "https://api.shakers.com/v1/ai_system/ai_faq_search",
        {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${API_KEY}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query,
                user_id: userId,
                i_am_a_developer: isDeveloper
            })
        }
    );
    return response.json();
}
```

## Support
- API Documentation: https://docs.shakers.com/api
- Support Email: api-support@shakers.com
- Status Page: https://status.shakers.com
- Community Forums: https://community.shakers.com 