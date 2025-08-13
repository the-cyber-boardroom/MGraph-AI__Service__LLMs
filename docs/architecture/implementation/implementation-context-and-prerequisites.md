# Implementation Context and Prerequisites

## 🎯 Project Overview

MGraph-AI__Service__LLMs is a production-ready LLM service that consolidates multiple previous implementations into a single, unified platform. This document provides essential context for LLMs implementing this system.

## 📚 Key Dependencies and Their Roles

### OSBot-Utils (Critical Dependency)
**Package**: `osbot-utils`  
**Purpose**: Provides Type-Safe runtime type checking system  
**Key Features**:
- `Type_Safe` base class for all schemas
- `@type_safe` decorator for method validation
- `Safe_Id`, `Safe_Str`, `Safe_Path` for validated primitives
- Automatic initialization of typed attributes
- Collection type safety (List, Dict, Set)

**Implementation Note**: NEVER use Pydantic BaseModel directly. Always use Type_Safe classes.

### OSBot-Fast-API
**Package**: `osbot-fast-api`  
**Purpose**: Type-Safe wrapper around FastAPI  
**Key Features**:
- Automatic Type_Safe ↔ BaseModel conversion
- Built-in middleware (CORS, API Key, HTTP Events)
- Route organization via `Fast_API_Routes` classes
- Method name to URL conversion (get_user__id → /get-user/{id})

**Implementation Pattern**:
```python
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes

class Routes_LLMs(Fast_API_Routes):
    tag = 'llms'
    
    def complete(self, request: Schema__LLM_Request):  # Type_Safe, not BaseModel!
        return response  # Returns Type_Safe, auto-converted to JSON
    
    def setup_routes(self):
        self.add_route_post(self.complete)
```

### OSBot-AWS
**Package**: `osbot-aws`  
**Purpose**: AWS service integrations  
**Key Components Used**:
- `S3__DB_Base` - Base class for S3-backed databases
- `S3__Key_Generator` - Temporal path generation
- `S3__Virtual_Storage` - Virtual file system on S3

### OSBot-Local-Stack
**Package**: `osbot-local-stack`  
**Purpose**: Local AWS service emulation for development  
**Usage**: Set `LOCALSTACK_ENABLED=true` for local development

## 🏗️ Existing Code Patterns to Reuse

### 1. Platform Engine Pattern (from CBR Athena)

The Platform Engine pattern is already proven and should be ported directly:

```python
# Base pattern to follow
class LLM__Platform_Engine(Type_Safe):
    llm_platform: str
    llm_provider: str
    llm_model: str
    llm_chat_completion: LLMs__Chat_Completion
    
    def execute_request(self):
        # Provider-specific implementation
        pass

class LLM__Chat_Completion__Resolve_Engine(Type_Safe):
    @cache_on_self
    def llms_platform_engines(self):
        return {
            'OpenRouter': LLM__Platform_Engine__OpenRouter,
            'Direct': LLM__Platform_Engine__Direct,
            # ... map platform names to engine classes
        }
    
    def map_provider(self, llm_chat_completion):
        # Resolve platform → provider → model
        # Return appropriate engine instance
```

### 2. S3 Cache Pattern (Current Implementation)

The current S3 cache with virtual storage is good, enhance it with:

```python
class LLM__Cache(Virtual_Storage__S3):
    root_folder: Safe_Str__File__Path = Safe_Str__File__Path('llm-cache/')
    
    # Current: Good S3 backend with index
    # Add: Temporal organization by model/date/hour
    # Add: Cache key normalization
    # Add: Hit tracking and analytics
```

### 3. Request Execution Pattern (from OSBot-LLMs)

```python
class LLM__Execute_Request(Type_Safe):
    def requests_post__streamed(self, url, json, headers=None):
        # Handles streaming responses
        # Parse SSE format: "data: {...}"
        
    def requests_post__not_streamed(self, url, json, headers=None):
        # Standard POST request
        # Returns parsed content
```

## 🔑 Critical Implementation Details

### Type_Safe Usage Rules

1. **Always inherit from Type_Safe**:
```python
# ✅ CORRECT
class Schema__Model(Type_Safe):
    model_id: str
    name: str

# ❌ WRONG
from pydantic import BaseModel
class Schema__Model(BaseModel):  # Never do this!
```

2. **Type annotations are mandatory**:
```python
# ✅ CORRECT
class Config(Type_Safe):
    host: str
    port: int
    items: List[str]  # Specific types

# ❌ WRONG
class Config(Type_Safe):
    host = "localhost"  # Missing annotation
    items: list  # Untyped collection
```

3. **Use @type_safe for validation**:
```python
class Service(Type_Safe):
    @type_safe
    def process(self, data: Dict[str, Any]) -> Schema__Response:
        # Parameters and return validated at runtime
```

### FastAPI Integration Pattern

```python
# Main application setup
fast_api = Fast_API(
    enable_cors=True,
    enable_api_key=True,
    base_path='/api'
)
fast_api.setup()  # Must call before adding routes
fast_api.add_routes(Routes_LLMs)
fast_api.add_routes(Routes_Registry)
app = fast_api.app()  # Get FastAPI instance

# Lambda handler
from mangum import Mangum
handler = Mangum(app)
```

### Environment Variables

```bash
# API Keys (Provider-specific)
OPEN_ROUTER_API_KEY=or-...
OPEN_AI__API_KEY=sk-...
GROQ_API_KEY=gsk_...
MISTRAL_API_KEY=...
TOGETHER_AI_API_KEY=...
SAMBANOVA_API_KEY=...

# LocalStack (Development)
LOCALSTACK_ENABLED=true
AWS_ENDPOINT_URL=http://localhost:4566

# FastAPI Configuration
FAST_API__AUTH__API_KEY__NAME=X-API-Key
FAST_API__AUTH__API_KEY__VALUE=your-secret-key

# Cache Configuration
LLM__CACHE__BUCKET_NAME__PREFIX=service-llm-cache
LLM__CACHE__BUCKET_NAME__SUFFIX=data

# Ollama (Local)
OLLAMA__BASE_URL=http://localhost:11434
```

## 🚫 Common Pitfalls to Avoid

### 1. Mixing Type Systems
```python
# ❌ WRONG - Mixing Pydantic with Type_Safe
class BadSchema(Type_Safe, BaseModel):
    pass

# ✅ CORRECT - Use Type_Safe only
class GoodSchema(Type_Safe):
    pass
```

### 2. Direct FastAPI Usage
```python
# ❌ WRONG - Using FastAPI directly
from fastapi import FastAPI
app = FastAPI()

@app.get("/endpoint")
def endpoint():
    pass

# ✅ CORRECT - Use Fast_API wrapper
from osbot_fast_api.api.Fast_API import Fast_API
fast_api = Fast_API()
fast_api.setup()
```

### 3. Incorrect Route Definition
```python
# ❌ WRONG - Using decorators
class Routes(Fast_API_Routes):
    @router.get("/endpoint")  # Don't use decorators
    def endpoint(self):
        pass

# ✅ CORRECT - Use setup_routes
class Routes(Fast_API_Routes):
    def endpoint(self):
        pass
    
    def setup_routes(self):
        self.add_route_get(self.endpoint)
```

## 📁 Project Structure

```
mgraph_ai_service_llms/
├── config.py                      # Configuration constants
├── fast_api/
│   ├── Service__Fast_API.py      # Main FastAPI setup
│   ├── routes/
│   │   ├── Routes__LLMs.py       # LLM endpoints
│   │   ├── Routes__Registry.py   # Model registry endpoints
│   │   ├── Routes__Cache.py      # Cache management
│   │   └── Routes__Admin.py      # Admin endpoints
├── service/
│   ├── core/
│   │   ├── engine/
│   │   │   ├── LLM__Platform_Engine.py
│   │   │   └── LLM__Engine_Resolver.py
│   │   └── execution/
│   │       └── LLM__Execute_Request.py
│   ├── providers/
│   │   ├── base/
│   │   │   └── LLM__Provider__Base.py
│   │   ├── implementations/
│   │   │   ├── LLM__OpenRouter.py
│   │   │   ├── LLM__OpenAI.py
│   │   │   ├── LLM__Groq.py
│   │   │   └── LLM__Ollama.py
│   │   └── engines/
│   │       ├── Engine__OpenRouter.py
│   │       ├── Engine__Direct.py
│   │       └── Engine__Local.py
│   ├── registry/
│   │   ├── Service__Model_Registry.py
│   │   └── schemas/
│   │       ├── Schema__Platform.py
│   │       ├── Schema__Provider.py
│   │       └── Schema__Model.py
│   ├── cache/
│   │   ├── LLM__Cache.py
│   │   ├── Service__Cache.py
│   │   └── Cache__Key_Generator.py
│   └── schemas/
│       ├── Schema__LLM_Request.py
│       ├── Schema__LLM_Response.py
│       └── Schema__Cache_Entry.py
└── utils/
    ├── LocalStack__Setup.py
    └── Version.py
```

## 🧪 Testing Approach

### Unit Tests
```python
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server

def test_llm_complete():
    fast_api = Fast_API()
    fast_api.setup()
    fast_api.add_routes(Routes_LLMs)
    
    with Fast_API_Server(app=fast_api.app()) as server:
        response = server.requests_post(
            '/llms/complete',
            data={'prompt': 'test', 'model': 'gpt-5-nano'}
        )
        assert response.status_code == 200
```

### Integration Tests
- Use LocalStack for S3 operations
- Mock external API calls
- Test with real Type_Safe conversions

## 🔄 Migration Notes

### From Current Implementation
- Keep: S3 cache structure, Virtual Storage
- Enhance: Add temporal organization, hit tracking
- Keep: OpenRouter provider implementation
- Add: More providers using Platform Engine pattern

### From OSBot-LLMs
- Port: Platform Engine pattern (proven design)
- Port: Streaming response handling
- Port: Multiple provider support
- Skip: Complex chat thread management (for now)

### From OSBot-Utils LLMs
- Use: Type-Safe schemas throughout
- Use: Cache path generation utilities
- Use: Request builder pattern (adapt for multiple providers)
- Skip: SQLite cache backend (S3 is sufficient)

## 🎯 Implementation Priorities

1. **Core Infrastructure** (Must Have)
   - Platform Engine base classes
   - Engine Resolver
   - Type_Safe schemas
   - Basic API structure

2. **Essential Providers** (Must Have)
   - OpenRouter (already exists, enhance)
   - OpenAI (reference implementation)
   - Groq (free tier)

3. **Model Registry** (Should Have)
   - S3-backed configuration
   - CRUD APIs
   - Cost tracking

4. **Advanced Features** (Nice to Have)
   - Schema I/O endpoints
   - Batch processing
   - Cache analytics
   - Admin UI

## 📝 Code Generation Instructions for LLMs

When implementing this system:

1. **Always use Type_Safe**, never Pydantic BaseModel
2. **Follow the Platform → Provider → Model hierarchy**
3. **Use Fast_API_Routes for endpoints**, not FastAPI decorators
4. **Implement setup_routes() method** in route classes
5. **Use environment variables** for all configuration
6. **Cache all LLM requests** using the S3 backend
7. **Generate deterministic cache keys** for consistent caching
8. **Handle streaming and non-streaming** responses
9. **Validate everything with @type_safe** decorator
10. **Follow existing patterns** from CBR Athena for engines

## 🔗 References

- OSBot-Utils Type_Safe: Runtime type safety throughout
- OSBot-Fast-API: Type-Safe FastAPI wrapper
- Platform Engine Pattern: From CBR Athena implementation
- S3 Virtual Storage: Current cache implementation
- Environment Variables: Configuration management