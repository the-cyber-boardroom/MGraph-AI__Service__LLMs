# Complete Schemas Reference

## 🎯 Overview

This document provides all Type_Safe schemas needed for the MGraph-AI__Service__LLMs implementation. These schemas define the complete data model for the system.

## 📋 Core Request/Response Schemas

### LLM Request Schema

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from typing import List, Optional, Dict, Any
from datetime import datetime

class Schema__LLM_Message(Type_Safe):
    role: str  # "system", "user", "assistant"
    content: str
    images: Optional[List[str]] = None  # URLs or base64
    metadata: Optional[Dict[str, Any]] = None

class Schema__LLM_Function(Type_Safe):
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema
    required: List[str] = []

class Schema__LLM_Request(Type_Safe):
    # Model selection
    model_id: str
    platform: Optional[str] = None  # If None, use best route
    provider: Optional[str] = None
    
    # Message content
    messages: List[Schema__LLM_Message]
    
    # Generation parameters
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
    
    # Advanced features
    functions: Optional[List[Schema__LLM_Function]] = None
    function_call: Optional[str] = None  # "auto", "none", or function name
    response_format: Optional[Dict[str, Any]] = None  # For structured output
    
    # Streaming
    stream: bool = False
    
    # Metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    tags: List[str] = []
    
    # Cache control
    use_cache: bool = True
    cache_ttl_hours: Optional[int] = None
```

### LLM Response Schema

```python
class Schema__LLM_Choice(Type_Safe):
    index: int
    message: Schema__LLM_Message
    finish_reason: str  # "stop", "length", "function_call", etc.
    
class Schema__LLM_Usage(Type_Safe):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
class Schema__LLM_Cost(Type_Safe):
    input_cost: float
    output_cost: float
    total_cost: float
    currency: str = "USD"

class Schema__LLM_Response(Type_Safe):
    # Core response
    choices: List[Schema__LLM_Choice]
    model: str
    
    # Usage and cost
    usage: Schema__LLM_Usage
    cost: Schema__LLM_Cost
    
    # Metadata
    response_id: str
    created_at: datetime
    platform_used: str
    provider_used: str
    
    # Performance
    latency_ms: float
    cache_hit: bool = False
    
    # Function calling
    function_name: Optional[str] = None
    function_arguments: Optional[Dict[str, Any]] = None
    
    # Raw response (for debugging)
    raw_response: Optional[Dict[str, Any]] = None
```

## 🏗️ Model Registry Schemas

### Platform Schema

```python
class Schema__Platform_Auth(Type_Safe):
    type: str  # "api_key", "oauth", "none"
    env_var: Optional[str] = None
    header_name: Optional[str] = None
    config: Dict[str, Any] = {}

class Schema__Platform_Features(Type_Safe):
    streaming: bool = False
    batch: bool = False
    async_requests: bool = False
    rate_limiting: bool = True
    custom_endpoints: bool = False

class Schema__Platform(Type_Safe):
    # Identity
    platform_id: str
    name: str
    description: str
    
    # API Configuration
    base_url: str
    auth: Schema__Platform_Auth
    timeout_seconds: int = 30
    max_retries: int = 3
    
    # Capabilities
    features: Schema__Platform_Features
    supported_providers: List[str]
    
    # Status
    status: str  # "active", "beta", "deprecated", "maintenance"
    health_check_url: Optional[str] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: str = "1.0.0"
    tags: List[str] = []
```

### Provider Schema

```python
class Schema__Provider_Capabilities(Type_Safe):
    vision: bool = False
    audio: bool = False
    streaming: bool = False
    function_calling: bool = False
    embeddings: bool = False
    fine_tuning: bool = False
    
class Schema__Provider(Type_Safe):
    # Identity
    provider_id: str
    name: str
    description: str
    
    # Access
    platforms: List[str]  # Available on these platforms
    direct_api_url: Optional[str] = None
    requires_auth: bool = True
    
    # Capabilities
    capabilities: Schema__Provider_Capabilities
    
    # Models
    model_families: List[str] = []  # e.g., ["gpt", "whisper", "dall-e"]
    model_count: int = 0
    
    # Status
    status: str  # "active", "beta", "deprecated"
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    website: Optional[str] = None
    documentation_url: Optional[str] = None
```

### Model Schema

```python
class Schema__Model_Capabilities(Type_Safe):
    vision: bool = False
    audio: bool = False
    streaming: bool = True
    function_calling: bool = False
    json_mode: bool = False
    system_messages: bool = True
    multi_turn: bool = True

class Schema__Model_Limits(Type_Safe):
    context_window: int
    max_output_tokens: int
    max_images: Optional[int] = None
    max_functions: Optional[int] = None
    rate_limit_rpm: Optional[int] = None  # Requests per minute
    rate_limit_tpm: Optional[int] = None  # Tokens per minute

class Schema__Model_Pricing(Type_Safe):
    input_cost_per_million: float
    output_cost_per_million: float
    image_cost_per_image: Optional[float] = None
    audio_cost_per_minute: Optional[float] = None
    currency: str = "USD"
    free_tier_tokens: Optional[int] = None

class Schema__Model_Performance(Type_Safe):
    avg_latency_ms: float
    tokens_per_second: float
    time_to_first_token_ms: Optional[float] = None
    
class Schema__Model(Type_Safe):
    # Identity
    model_id: str
    provider_id: str
    name: str
    model_string: str  # API parameter value
    family: str  # e.g., "gpt", "claude", "llama"
    version: str
    
    # Description
    description: str
    use_cases: List[str] = []
    
    # Capabilities
    capabilities: Schema__Model_Capabilities
    limits: Schema__Model_Limits
    
    # Pricing
    pricing: Schema__Model_Pricing
    
    # Performance
    performance: Schema__Model_Performance
    
    # Platform configurations
    platform_configs: Dict[str, Dict[str, Any]] = {}
    
    # Status
    status: str  # "active", "beta", "deprecated", "sunset"
    release_date: Optional[datetime] = None
    deprecation_date: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    migration_to: Optional[str] = None  # Suggested replacement model
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []  # e.g., ["free", "fast", "accurate", "multimodal"]
```

### Route Schema

```python
class Schema__Route_Config(Type_Safe):
    endpoint_override: Optional[str] = None
    model_string_override: Optional[str] = None
    headers_override: Optional[Dict[str, str]] = None
    timeout_override: Optional[int] = None

class Schema__Route_Performance(Type_Safe):
    success_rate: float = 1.0
    avg_latency_ms: float = 0.0
    total_requests: int = 0
    failed_requests: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None

class Schema__Route(Type_Safe):
    # Identity
    route_id: str
    model_id: str
    platform_id: str
    provider_id: str
    
    # Configuration
    config: Schema__Route_Config
    
    # Priority and status
    priority: int  # 1 = primary, higher = fallback
    status: str  # "active", "inactive", "maintenance"
    enabled: bool = True
    
    # Performance tracking
    performance: Schema__Route_Performance
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    notes: Optional[str] = None
```

## 💾 Cache Schemas

### Cache Entry Schema

```python
class Schema__Cache_Request(Type_Safe):
    model: str
    messages: List[Dict[str, Any]]
    temperature: float
    max_tokens: Optional[int]
    normalized_hash: str

class Schema__Cache_Metadata(Type_Safe):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    platform: str
    provider: str
    model: str
    tags: List[str] = []

class Schema__Cache_Entry(Type_Safe):
    # Identity
    cache_id: str
    cache_key: str
    request_hash: str
    
    # Request/Response
    request: Schema__Cache_Request
    response: Schema__LLM_Response
    
    # Timestamps
    created_at: datetime
    last_accessed: datetime
    expires_at: Optional[datetime] = None
    
    # Usage tracking
    hit_count: int = 0
    cost_saved: float = 0.0
    
    # Metadata
    metadata: Schema__Cache_Metadata
    
    # Storage
    storage_path: str
    size_bytes: int
    compressed: bool = False
    encrypted: bool = False
```

### Cache Index Schema

```python
class Schema__Cache_Index(Type_Safe):
    # Lookup maps
    cache_id_by_hash: Dict[str, str]  # hash -> cache_id
    cache_path_by_id: Dict[str, str]  # cache_id -> S3 path
    
    # Statistics
    total_entries: int = 0
    total_size_bytes: int = 0
    total_hits: int = 0
    total_cost_saved: float = 0.0
    
    # Metadata
    last_updated: datetime
    version: str = "1.0.0"
```

## 📊 Analytics Schemas

### Usage Analytics Schema

```python
class Schema__Usage_By_Model(Type_Safe):
    model_id: str
    request_count: int
    token_count: Schema__LLM_Usage
    total_cost: float
    cache_hits: int
    cache_hit_rate: float
    avg_latency_ms: float

class Schema__Usage_By_Platform(Type_Safe):
    platform_id: str
    request_count: int
    total_cost: float
    success_rate: float
    avg_latency_ms: float

class Schema__Usage_Analytics(Type_Safe):
    # Time period
    start_date: datetime
    end_date: datetime
    
    # Overall metrics
    total_requests: int
    total_tokens: Schema__LLM_Usage
    total_cost: float
    cache_hit_rate: float
    
    # Breakdowns
    by_model: List[Schema__Usage_By_Model]
    by_platform: List[Schema__Usage_By_Platform]
    by_user: Dict[str, Dict[str, Any]]
    
    # Trends
    daily_requests: List[Dict[str, Any]]
    daily_costs: List[Dict[str, Any]]
    
    # Savings
    cache_cost_saved: float
    optimal_route_savings: float
```

## 🔄 Transformation Schemas

### Schema Transform Request

```python
class Schema__Transform_Request(Type_Safe):
    # Input
    input_schema: str  # Schema name or inline definition
    input_data: Dict[str, Any]
    
    # Output
    output_schema: str  # Schema name or inline definition
    
    # Transformation hints
    mapping_hints: Optional[Dict[str, str]] = None
    validation_strict: bool = True
    
    # Model selection
    model_id: Optional[str] = None  # Use default if not specified
    temperature: float = 0.3  # Lower for consistency
```

### Batch Processing Schema

```python
class Schema__Batch_Item(Type_Safe):
    item_id: str
    request: Schema__LLM_Request
    priority: int = 5  # 1-10, 1 = highest
    timeout_seconds: Optional[int] = None

class Schema__Batch_Request(Type_Safe):
    batch_id: str
    items: List[Schema__Batch_Item]
    
    # Execution settings
    parallel: bool = True
    max_concurrent: int = 5
    stop_on_error: bool = False
    
    # Model settings (override item settings)
    model_id: Optional[str] = None
    platform: Optional[str] = None

class Schema__Batch_Result(Type_Safe):
    batch_id: str
    items: List[Dict[str, Any]]  # item_id -> response
    
    # Statistics
    total_items: int
    successful: int
    failed: int
    total_tokens: Schema__LLM_Usage
    total_cost: float
    total_time_ms: float
    
    # Errors
    errors: List[Dict[str, Any]] = []
```

## 🛡️ Admin Schemas

### System Health Schema

```python
class Schema__Service_Health(Type_Safe):
    service: str
    status: str  # "healthy", "degraded", "down"
    latency_ms: Optional[float] = None
    last_check: datetime
    error: Optional[str] = None

class Schema__System_Health(Type_Safe):
    overall_status: str  # "healthy", "degraded", "down"
    services: List[Schema__Service_Health]
    
    # Metrics
    uptime_seconds: int
    request_rate: float  # per second
    error_rate: float
    
    # Resources
    cache_usage_percent: float
    memory_usage_mb: int
    
    # Timestamp
    checked_at: datetime
```

### Configuration Schema

```python
class Schema__Cache_Config(Type_Safe):
    enabled: bool = True
    ttl_hours: int = 168
    max_size_gb: float = 100.0
    eviction_strategy: str = "lru"

class Schema__RateLimit_Config(Type_Safe):
    enabled: bool = True
    requests_per_minute: int = 100
    tokens_per_minute: int = 100000
    burst_size: int = 10

class Schema__Fallback_Config(Type_Safe):
    enabled: bool = True
    max_retries: int = 3
    timeout_ms: int = 30000
    backoff_multiplier: float = 2.0

class Schema__System_Config(Type_Safe):
    cache: Schema__Cache_Config
    rate_limiting: Schema__RateLimit_Config
    fallback: Schema__Fallback_Config
    
    # Feature flags
    features: Dict[str, bool] = {
        "streaming": True,
        "batch_processing": True,
        "cost_tracking": True,
        "admin_api": True
    }
    
    # Defaults
    default_model: str = "gpt-5-nano"
    default_platform: str = "openrouter"
    default_temperature: float = 0.7
```

## 🔐 Security Schemas

```python
class Schema__API_Key(Type_Safe):
    key_id: str
    key_hash: str  # Never store plain key
    name: str
    
    # Permissions
    scopes: List[str]  # e.g., ["llm:complete", "registry:read"]
    rate_limit_override: Optional[int] = None
    
    # Metadata
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    
    # Status
    active: bool = True
    revoked: bool = False
    revoked_reason: Optional[str] = None
```

## 📝 Implementation Notes for LLMs

1. **All schemas inherit from Type_Safe**, never from BaseModel or dataclass
2. **Use Optional[] for nullable fields** with default None
3. **Use List[] not list**, Dict[] not dict for type safety
4. **Datetime fields** use Python's datetime type
5. **Default values** can be set directly in class definition
6. **Nested Type_Safe objects** work automatically
7. **Collections of Type_Safe objects** are fully supported
8. **@type_safe decorator** validates method parameters and returns
9. **Auto-initialization** handles all typed fields
10. **JSON serialization** via .json() method on any Type_Safe instance

These schemas provide the complete data model for the MGraph-AI__Service__LLMs system. They ensure type safety throughout the application and automatic validation at runtime.