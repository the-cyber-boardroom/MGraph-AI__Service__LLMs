# Model Registry Design

## 📊 Overview

The Model Registry is a dynamic, API-driven system for managing LLM platforms, providers, and models. It serves as the single source of truth for all model configurations, capabilities, and pricing.

## 🗄️ Data Model

### Platform Schema

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from typing import List, Dict, Optional
from datetime import datetime

class Schema__Platform(Type_Safe):
    platform_id: str              # e.g., "openrouter", "direct", "local"
    name: str                     # Display name
    description: str              # Platform description
    base_url: str                 # API endpoint
    auth_type: str                # "api_key", "oauth", "none"
    auth_config: Dict[str, str]   # Auth configuration
    supported_providers: List[str] # List of provider IDs
    features: Dict[str, bool]     # Platform capabilities
    status: str                   # "active", "beta", "deprecated"
    created_at: datetime
    updated_at: datetime
```

### Provider Schema

```python
class Schema__Provider(Type_Safe):
    provider_id: str              # e.g., "openai", "mistral", "meta"
    name: str                     # Display name
    description: str              # Provider description
    platforms: List[str]          # Available on these platforms
    direct_api_url: Optional[str] # Direct API if available
    auth_required: bool           # Needs authentication
    features: Dict[str, bool]     # Provider capabilities
    status: str                   # "active", "beta", "deprecated"
    created_at: datetime
    updated_at: datetime
```

### Model Schema

```python
class Schema__Model(Type_Safe):
    model_id: str                 # Unique identifier
    provider_id: str              # Parent provider
    name: str                     # Display name
    model_string: str             # API model string
    description: str              # Model description
    
    # Capabilities
    capabilities: Dict[str, bool]  # vision, audio, streaming, etc.
    context_window: int           # Max tokens
    max_output_tokens: int        # Max response tokens
    
    # Pricing (per million tokens)
    pricing: Dict[str, float]     # input_cost, output_cost
    
    # Platform-specific configurations
    platform_configs: Dict[str, Dict] # Platform-specific settings
    
    # Performance characteristics
    performance: Dict[str, float] # latency_ms, tokens_per_second
    
    # Metadata
    version: str                  # Model version
    release_date: Optional[datetime]
    deprecation_date: Optional[datetime]
    status: str                   # "active", "beta", "deprecated"
    tags: List[str]              # Free, fast, powerful, etc.
    
    created_at: datetime
    updated_at: datetime
```

### Route Configuration Schema

```python
class Schema__Route(Type_Safe):
    route_id: str                 # Unique route identifier
    model_id: str                 # Target model
    platform_id: str              # Via this platform
    provider_id: str              # From this provider
    
    # Route specifics
    endpoint_override: Optional[str]  # Custom endpoint
    model_string_override: Optional[str]  # Platform-specific model string
    
    # Route metadata
    priority: int                 # For fallback chains (1 = primary)
    status: str                   # "active", "inactive", "maintenance"
    
    # Performance tracking
    success_rate: float           # Historical success rate
    avg_latency_ms: float         # Average response time
    
    created_at: datetime
    updated_at: datetime
```

## 🔄 Registry Operations

### CRUD APIs

```python
class Service__Model_Registry(Type_Safe):
    
    # Platform Operations
    def create_platform(self, platform: Schema__Platform) -> str
    def get_platform(self, platform_id: str) -> Schema__Platform
    def update_platform(self, platform_id: str, updates: Dict) -> bool
    def delete_platform(self, platform_id: str) -> bool
    def list_platforms(self, status: Optional[str] = None) -> List[Schema__Platform]
    
    # Provider Operations
    def create_provider(self, provider: Schema__Provider) -> str
    def get_provider(self, provider_id: str) -> Schema__Provider
    def update_provider(self, provider_id: str, updates: Dict) -> bool
    def delete_provider(self, provider_id: str) -> bool
    def list_providers(self, platform_id: Optional[str] = None) -> List[Schema__Provider]
    
    # Model Operations
    def create_model(self, model: Schema__Model) -> str
    def get_model(self, model_id: str) -> Schema__Model
    def update_model(self, model_id: str, updates: Dict) -> bool
    def delete_model(self, model_id: str) -> bool
    def list_models(self, filters: Dict) -> List[Schema__Model]
    
    # Route Operations
    def create_route(self, route: Schema__Route) -> str
    def get_routes_for_model(self, model_id: str) -> List[Schema__Route]
    def update_route_priority(self, route_id: str, priority: int) -> bool
    def get_best_route(self, model_id: str) -> Schema__Route
```

## 💾 S3 Storage Structure

```
s3://mgraph-ai-llm-registry/
├── platforms/
│   ├── openrouter.json
│   ├── direct.json
│   └── local.json
├── providers/
│   ├── openai.json
│   ├── mistral.json
│   ├── meta.json
│   └── google.json
├── models/
│   ├── by-provider/
│   │   ├── openai/
│   │   │   ├── gpt-5-nano.json
│   │   │   ├── gpt-5-mini.json
│   │   │   └── gpt-4o.json
│   │   └── mistral/
│   │       ├── mistral-small.json
│   │       └── mistral-large.json
│   └── by-platform/
│       ├── openrouter/
│       └── direct/
├── routes/
│   ├── by-model/
│   │   └── gpt-5-nano/
│   │       ├── route-1-direct.json
│   │       └── route-2-openrouter.json
│   └── by-platform/
└── metadata/
    ├── index.json           # Fast lookup index
    ├── capabilities.json    # Capability matrix
    └── pricing.json        # Current pricing
```

## 🔍 Query Patterns

### Find Models by Capability

```python
def find_models_with_capabilities(
    required: List[str],     # Must have these
    optional: List[str],     # Nice to have
    excluded: List[str]      # Must not have
) -> List[Schema__Model]:
    """Find models matching capability requirements"""
```

### Find Cheapest Route

```python
def find_cheapest_route_for_prompt(
    prompt_tokens: int,
    max_output_tokens: int,
    required_capabilities: List[str]
) -> Tuple[Schema__Route, float]:
    """Find most cost-effective route for a request"""
```

### Get Platform Availability

```python
def get_model_availability(
    model_id: str
) -> Dict[str, List[Schema__Route]]:
    """Get all platforms where model is available"""
```

## 🔄 Update Mechanisms

### Automatic Updates

- **Pricing Updates**: Daily sync from provider APIs
- **Status Monitoring**: Health checks every 5 minutes
- **Performance Metrics**: Calculated from actual usage
- **Deprecation Notices**: Check provider announcements

### Manual Updates via API

```python
# Update model pricing
PATCH /api/registry/models/{model_id}/pricing
{
    "input_cost": 0.05,
    "output_cost": 0.15
}

# Add new capability
PATCH /api/registry/models/{model_id}/capabilities
{
    "operation": "add",
    "capability": "function_calling",
    "value": true
}

# Deprecate model
PATCH /api/registry/models/{model_id}/status
{
    "status": "deprecated",
    "deprecation_date": "2024-12-31",
    "migration_guide": "Use gpt-5-mini instead"
}
```

## 🎯 Registry Features

### Model Discovery

- Browse by capability
- Filter by price range
- Search by context window
- Find alternatives to deprecated models

### Cost Optimization

- Compare prices across platforms
- Calculate request costs
- Suggest cheaper alternatives
- Track spending by model/platform

### Capability Matrix

```python
{
    "vision": ["gpt-4o", "claude-3-opus", "gemini-pro"],
    "audio": ["whisper-3", "gpt-4o"],
    "streaming": ["gpt-5-nano", "claude-3", "llama-3"],
    "function_calling": ["gpt-4o", "mistral-large"],
    "128k_context": ["claude-3", "gpt-4-turbo"],
    "free_tier": ["llama-3-8b", "mistral-7b", "phi-2"]
}
```

### Fallback Chains

```python
{
    "gpt-5-nano": [
        {"platform": "direct", "priority": 1},
        {"platform": "openrouter", "priority": 2},
        {"platform": "azure", "priority": 3}
    ]
}
```

## 📡 Registry API Endpoints

### Platforms
- `GET /api/registry/platforms` - List all platforms
- `GET /api/registry/platforms/{id}` - Get platform details
- `POST /api/registry/platforms` - Create platform
- `PATCH /api/registry/platforms/{id}` - Update platform
- `DELETE /api/registry/platforms/{id}` - Delete platform

### Providers
- `GET /api/registry/providers` - List all providers
- `GET /api/registry/providers/{id}` - Get provider details
- `POST /api/registry/providers` - Create provider
- `PATCH /api/registry/providers/{id}` - Update provider
- `DELETE /api/registry/providers/{id}` - Delete provider

### Models
- `GET /api/registry/models` - List models with filters
- `GET /api/registry/models/{id}` - Get model details
- `POST /api/registry/models` - Create model
- `PATCH /api/registry/models/{id}` - Update model
- `DELETE /api/registry/models/{id}` - Delete model
- `GET /api/registry/models/{id}/routes` - Get available routes

### Discovery
- `GET /api/registry/search` - Search models
- `GET /api/registry/capabilities` - Get capability matrix
- `GET /api/registry/pricing` - Get pricing comparison
- `POST /api/registry/recommend` - Get model recommendations