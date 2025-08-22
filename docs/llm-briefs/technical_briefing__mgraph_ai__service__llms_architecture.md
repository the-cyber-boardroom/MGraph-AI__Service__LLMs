# Technical Briefing: MGraph-AI__Service__LLMs Architecture

## Project Overview

MGraph-AI__Service__LLMs is a high-performance LLM service layer that provides unified access to multiple LLM providers through a FastAPI-based REST API. The service implements sophisticated caching, provider routing, and cost optimization strategies while maintaining clean separation of concerns across its architecture.

## Core Architecture Components

### 1. Service Layer Structure

The project follows a three-tier architecture:

```
Routes Layer (FastAPI endpoints)
    ↓
Service Layer (Business logic)
    ↓
Provider Layer (External APIs)
```

**Key Services:**
- `Service__Open_Router`: Manages OpenRouter API interactions with multi-provider routing
- `Service__LLM__Simple`: Simplified interface for common LLM operations
- `Service__Text_Analysis`: Specialized text extraction and analysis utilities
- `Service__Performance`: Performance testing and benchmarking infrastructure
- `Service__Cache`: S3-based caching with temporal and latest patterns

### 2. Provider Management

The system uses OpenRouter as a meta-provider, enabling:
- **Dynamic Provider Routing**: Routes requests to Groq, Cerebras, Together, DeepInfra based on availability and performance
- **Cost Optimization**: Tracks and estimates costs per request with provider-specific pricing
- **Fallback Strategies**: Automatic failover when providers are unavailable
- **Provider Preferences**: Fine-grained control via `Schema__Open_Router__Provider_Preferences`

## Integration with OSBot-Fast-API

### Dependency Relationship

MGraph-AI__Service__LLMs extends OSBot-Fast-API's capabilities:

```python
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes

class Service__Fast_API(Serverless__Fast_API):
    # Inherits route management, middleware, and serverless deployment
```

### Key Integration Points

1. **Route Management**: Uses OSBot-Fast-API's automatic route registration
   - Type-safe route definitions
   - Automatic OpenAPI documentation generation
   - Consistent error handling

2. **Serverless Deployment**: Leverages `Serverless__Fast_API` for AWS Lambda deployment
   - Handler generation for Lambda
   - Dependency packaging
   - LocalStack testing support

3. **Configuration Management**: Inherits configuration patterns
   - Environment variable handling
   - Safe string types for validation
   - Structured settings management

## Integration with Memory-FS

### Caching Architecture

Memory-FS provides the sophisticated caching layer:

```python
from memory_fs.helpers.Memory_FS__Latest_Temporal import Memory_FS__Latest_Temporal
from memory_fs.storage_fs.Storage_FS import Storage_FS

class Open_Router__Cache:
    fs__latest_temporal: Memory_FS__Latest_Temporal  # Temporal + latest patterns
    s3__storage: Storage_FS__S3                      # S3 backend
```

### Cache Patterns Implemented

1. **Latest Pattern**: Most recent response for each unique request
2. **Temporal Pattern**: Time-based cache organization (year/month/day/hour structure)
3. **Combined Pattern**: Both latest and temporal for comprehensive cache management

### Storage Backend

**S3 Integration via Storage_FS__S3:**
- Bucket structure: `service-llm-cache-data/`
- File organization: `model_name/2025/01/23/15/cache_id.json`
- Metadata tracking for TTL and request hashing
- LocalStack support for development

## Key Design Patterns

### 1. Type Safety Throughout

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Service__LLM__Simple(Type_Safe):
    model: str = DEFAULT_MODEL  # Type-enforced configuration
```

### 2. Request/Response Schemas

Strong typing for all API interactions:
- `Schema__Open_Router__Chat_Request`: Structured request format
- `Schema__Open_Router__Provider_Preferences`: Provider routing configuration
- `Schema__Facts`, `Schema__Fact`: Structured extraction results

### 3. Cache-First Architecture

Every LLM request follows:
1. Generate request hash
2. Check cache (Memory-FS)
3. If miss, make API call
4. Store in cache with TTL
5. Return response

## Performance Optimizations

### Caching Strategy
- **Request Hashing**: SHA-256 of complete request for cache keys
- **TTL Management**: 24-hour default for chat responses
- **Cache Hit Rates**: Typically 40-60% for repeated queries

### Provider Optimization
- **GROQ Default**: Selected for 1000+ tokens/second throughput
- **Smart Routing**: Automatic selection based on model and availability
- **Cost Tracking**: Real-time cost calculation and limits

## Deployment Architecture

### AWS Lambda Configuration
```python
LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS = [
    'osbot-fast-api-serverless==v1.12.0',
    'osbot-local-stack==0.5.0',
    'memory-fs==0.17.0'
]
```

### LocalStack Development
- Full AWS service emulation
- S3 bucket creation and management
- Lambda function testing
- No cloud costs during development

## API Structure

### Route Organization
```
/info/*                    - Service health and status
/llms/*                    - Core LLM operations
/cache/*                   - Cache management
/performance/*             - Performance testing
/llm-simple/*             - Simplified LLM interface
/text-analysis/*          - Text extraction utilities
/platform/open-router/*   - Provider-specific operations
```

### Consistent Response Format
```json
{
    "status": "success",
    "data": {...},
    "model": "openai/gpt-oss-120b",
    "provider": "groq",
    "duration_seconds": 1.234,
    "from_cache": false
}
```

## Testing Infrastructure

### Test Hierarchy
1. **Unit Tests**: Service logic validation
2. **Integration Tests**: Real API calls with LocalStack
3. **Route Tests**: FastAPI TestClient validation
4. **Performance Tests**: Throughput and latency benchmarking

### Test Data Management
- LocalStack for S3 simulation
- Temporary credentials for testing
- Automatic cleanup after tests

## Security Considerations

- **API Key Management**: Environment variables only, never in code
- **Request Validation**: Type-safe string classes prevent injection
- **Cost Controls**: Max cost limits per request
- **Provider Isolation**: Each provider connection isolated

## Monitoring and Observability

- **Request Tracking**: Unique request IDs throughout pipeline
- **Performance Metrics**: Duration tracking at each layer
- **Cache Statistics**: Hit rates, size, age tracking
- **Cost Analytics**: Per-request and aggregate cost tracking

This architecture provides a production-ready LLM service with enterprise features while maintaining development simplicity through the OSBot and Memory-FS frameworks.