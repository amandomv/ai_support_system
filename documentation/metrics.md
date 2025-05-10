# Metrics Documentation

## Overview
The AI Support System uses Prometheus for metrics collection and monitoring. The metrics system is designed to track performance, usage patterns, and system health.

## Core Metrics

### 1. Response Time Metrics
```python
# Example metric definition
RESPONSE_TIME = Histogram(
    'ai_support_response_time_seconds',
    'Time taken to generate AI support response',
    ['endpoint']
)
```

#### Available Metrics:
- `ai_support_response_time_seconds`: Time to generate support responses
- `recommendation_generation_time_seconds`: Time to generate recommendations
- `embedding_generation_time_seconds`: Time to generate embeddings

### 2. Usage Metrics
```python
# Example metric definition
QUERY_COUNT = Counter(
    'ai_support_queries_total',
    'Total number of queries processed',
    ['endpoint', 'status']
)
```

#### Available Metrics:
- `ai_support_queries_total`: Total queries processed
- `recommendation_requests_total`: Total recommendation requests
- `embedding_requests_total`: Total embedding generation requests

### 3. Error Metrics
```python
# Example metric definition
ERROR_COUNT = Counter(
    'ai_support_errors_total',
    'Total number of errors',
    ['endpoint', 'error_type']
)
```

#### Available Metrics:
- `ai_support_errors_total`: Total errors encountered
- `openai_api_errors_total`: OpenAI API specific errors
- `database_errors_total`: Database operation errors

## Metric Collection

### 1. Response Time Collection
```python
# Example usage
@metrics.track_time(RESPONSE_TIME, {'endpoint': 'support'})
async def get_ai_support_response(query: str):
    # Implementation
    pass
```

### 2. Usage Tracking
```python
# Example usage
@metrics.track_usage(QUERY_COUNT, {'endpoint': 'support'})
async def process_query(query: str):
    # Implementation
    pass
```

### 3. Error Tracking
```python
# Example usage
@metrics.track_errors(ERROR_COUNT, {'endpoint': 'support'})
async def handle_request(request: Request):
    # Implementation
    pass
```

## Prometheus Configuration

### 1. Basic Setup
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'ai_support'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
```

### 2. Metric Endpoints
- `/metrics`: Main metrics endpoint
- `/health`: Health check endpoint
- `/ready`: Readiness check endpoint

## Grafana Dashboards

### 1. Response Time Dashboard
- Average response time
- 95th percentile
- Response time distribution

### 2. Usage Dashboard
- Query volume
- Endpoint distribution
- Error rates

### 3. System Health Dashboard
- Error rates
- API availability
- Database performance

## Alerting Rules

### 1. Response Time Alerts
```yaml
# alert.rules
groups:
  - name: ai_support
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(ai_support_response_time_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
```

### 2. Error Rate Alerts
```yaml
# alert.rules
groups:
  - name: ai_support
    rules:
      - alert: HighErrorRate
        expr: rate(ai_support_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
```

## Best Practices

1. **Metric Naming**
   - Use consistent naming conventions
   - Include units in metric names
   - Use descriptive labels

2. **Label Usage**
   - Keep cardinality low
   - Use meaningful label values
   - Document label meanings

3. **Metric Types**
   - Use appropriate metric types
   - Consider aggregation needs
   - Plan for querying patterns

4. **Performance Impact**
   - Monitor metric collection overhead
   - Use efficient collection methods
   - Optimize storage requirements

## Common Issues and Solutions

1. **High Cardinality**
   - Limit label combinations
   - Use aggregation
   - Monitor label usage

2. **Storage Management**
   - Set retention policies
   - Use efficient storage
   - Regular cleanup

3. **Query Performance**
   - Optimize queries
   - Use appropriate functions
   - Monitor query times 