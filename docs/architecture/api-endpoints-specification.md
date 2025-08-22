# API Endpoints Specification

## 📋 Overview

This document defines all REST API endpoints for MGraph-AI__Service__LLMs, organized by functional area. All endpoints follow RESTful conventions and use Type_Safe schemas for request/response validation.

## 🔑 Authentication & Headers

All requests require:
```http
X-API-Key: {api_key}
Content-Type: application/json
```

Optional headers:
```http
X-Request-ID: {uuid}          # For request tracking
X-Cache-Control: no-cache     # Bypass cache
X-Cost-Limit: 1.00           # Max cost in USD
```

## 📚 API Categories

### 1️⃣ Simple LLM Operations (`/llms`)

These endpoints provide straightforward access to LLM capabilities with minimal configuration.

#### Text → Text
```http
POST /llms/complete
```
Simple text completion with optional model selection.

**Request:**
```json
{
  "prompt": "Explain quantum computing",
  "model": "gpt-5-nano",        // Optional, uses default if not specified
  "max_tokens": 500,             // Optional
  "temperature": 0.7             // Optional
}
```

**Response:**
```json
{
  "completion": "Quantum computing is...",
  "model_used": "gpt-5-nano",
  "tokens": {
    "prompt": 15,
    "completion": 247,
    "total": 262
  },
  "cost": {
    "amount": 0.0131,
    "currency": "USD"
  },
  "cache_hit": false,
  "request_id": "req_abc123"
}
```

#### Text → Schema
```http
POST /llms/extract
```
Extract structured data from text using Type_Safe schema.

**Request:**
```json
{
  "text": "John Doe, 30 years old, lives in New York",
  "schema": "Person",           // Name of registered Type_Safe schema
  "model": "gpt-4o-mini"
}
```

**Response:**
```json
{
  "data": {
    "name": "John Doe",
    "age": 30,
    "city": "New York"
  },
  "schema_version": "1.0",
  "validation_status": "valid",
  "model_used": "gpt-4o-mini",
  "cost": {...}
}
```

#### Schema → Text
```http
POST /llms/generate
```
Generate text from structured data.

**Request:**
```json
{
  "data": {
    "product": "iPhone 15",
    "features": ["5G", "A17 chip", "48MP camera"]
  },
  "template": "product_description",  // Template ID
  "model": "mistral-small"
}
```

**Response:**
```json
{
  "text": "The iPhone 15 represents the pinnacle of...",
  "template_used": "product_description_v2",
  "model_used": "mistral-small",
  "cost": {...}
}
```

#### Schema → Schema
```http
POST /llms/transform
```
Transform data from one schema to another.

**Request:**
```json
{
  "input_data": {...},
  "input_schema": "OrderV1",
  "output_schema": "InvoiceV2",
  "transformation_hints": "Include tax calculations",
  "model": "gpt-5-mini"
}
```

**Response:**
```json
{
  "output_data": {...},
  "transformation_log": [...],
  "validation_status": "valid",
  "model_used": "gpt-5-mini",
  "cost": {...}
}
```

### 2️⃣ Advanced LLM Operations (`/llms/advanced`)

#### Batch Processing
```http
POST /llms/batch
```
Process multiple requests in a single call.

**Request:**
```json
{
  "requests": [
    {"type": "complete", "prompt": "..."},
    {"type": "extract", "text": "...", "schema": "..."}
  ],
  "parallel": true,
  "max_cost": 5.00
}
```

#### Streaming
```http
POST /llms/stream
```
Stream responses using Server-Sent Events (SSE).

**Request:**
```json
{
  "prompt": "Write a long story about...",
  "model": "gpt-4o",
  "stream": true
}
```

**Response:** (SSE stream)
```
data: {"chunk": "Once upon a", "index": 0}
data: {"chunk": " time in a", "index": 1}
data: {"done": true, "total_tokens": 500}
```

#### Multi-Modal
```http
POST /llms/multimodal
```
Process text with images, audio, or other media.

**Request:**
```json
{
  "messages": [
    {"type": "text", "content": "What's in this image?"},
    {"type": "image", "url": "s3://bucket/image.jpg"}
  ],
  "model": "gpt-4o"
}
```

### 3️⃣ Model Registry Management (`/registry`)

#### Platforms

##### List Platforms
```http
GET /registry/platforms
```
Query parameters:
- `status`: active|beta|deprecated
- `features`: comma-separated list

**Response:**
```json
{
  "platforms": [
    {
      "platform_id": "openrouter",
      "name": "OpenRouter",
      "base_url": "https://openrouter.ai/api/v1",
      "auth_type": "api_key",
      "supported_providers": ["openai", "mistral", "meta"],
      "features": {
        "unified_billing": true,
        "fallback_routing": true
      },
      "status": "active"
    }
  ],
  "total": 3
}
```

##### Get Platform
```http
GET /registry/platforms/{platform_id}
```

##### Create Platform
```http
POST /registry/platforms
```
**Request:** Schema__Platform object

##### Update Platform
```http
PATCH /registry/platforms/{platform_id}
```
**Request:** Partial Schema__Platform

##### Delete Platform
```http
DELETE /registry/platforms/{platform_id}
```

#### Providers

##### List Providers
```http
GET /registry/providers
```
Query parameters:
- `platform_id`: Filter by platform
- `status`: active|beta|deprecated
- `features`: Required features

##### Get Provider
```http
GET /registry/providers/{provider_id}
```

##### Create Provider
```http
POST /registry/providers
```

##### Update Provider
```http
PATCH /registry/providers/{provider_id}
```

##### Delete Provider
```http
DELETE /registry/providers/{provider_id}
```

#### Models

##### List Models
```http
GET /registry/models
```
Query parameters:
- `provider_id`: Filter by provider
- `platform_id`: Available on platform
- `min_context`: Minimum context window
- `max_input_cost`: Maximum $/1M tokens
- `capabilities`: Required capabilities (vision,audio,streaming)
- `tags`: Filter by tags (free,fast,powerful)
- `sort`: cost|performance|context_window
- `limit`: Results per page
- `offset`: Pagination offset

**Response:**
```json
{
  "models": [
    {
      "model_id": "gpt-5-nano",
      "provider_id": "openai",
      "name": "GPT-5 Nano",
      "model_string": "openai/gpt-5-nano",
      "capabilities": {
        "vision": false,
        "audio": false,
        "streaming": true,
        "function_calling": true
      },
      "context_window": 400000,
      "max_output_tokens": 16000,
      "pricing": {
        "input_cost": 0.05,
        "output_cost": 0.40
      },
      "performance": {
        "latency_ms": 450,
        "tokens_per_second": 85
      },
      "tags": ["fast", "affordable"],
      "status": "active"
    }
  ],
  "total": 47,
  "page": 1,
  "pages": 5
}
```

##### Get Model
```http
GET /registry/models/{model_id}
```

##### Create Model
```http
POST /registry/models
```

##### Update Model
```http
PATCH /registry/models/{model_id}
```

##### Delete Model
```http
DELETE /registry/models/{model_id}
```

##### Get Model Routes
```http
GET /registry/models/{model_id}/routes
```
Get all available routes to access a model.

**Response:**
```json
{
  "model_id": "gpt-5-nano",
  "routes": [
    {
      "route_id": "route_001",
      "platform_id": "direct",
      "endpoint": "https://api.openai.com/v1/chat/completions",
      "priority": 1,
      "status": "active",
      "avg_latency_ms": 320
    },
    {
      "route_id": "route_002",
      "platform_id": "openrouter",
      "endpoint": "https://openrouter.ai/api/v1/chat/completions",
      "priority": 2,
      "status": "active",
      "avg_latency_ms": 380
    }
  ],
  "recommended_route": "route_001"
}
```

### 4️⃣ Discovery & Search (`/registry/discover`)

#### Search Models
```http
POST /registry/discover/search
```
Advanced model search with multiple criteria.

**Request:**
```json
{
  "query": "fast image analysis",
  "filters": {
    "capabilities": ["vision"],
    "max_cost": 1.00,
    "min_context_window": 32000
  },
  "sort": "performance",
  "limit": 10
}
```

#### Get Recommendations
```http
POST /registry/discover/recommend
```
Get model recommendations based on use case.

**Request:**
```json
{
  "use_case": "document_extraction",
  "requirements": {
    "accuracy": "high",
    "speed": "medium",
    "cost": "low"
  },
  "sample_data": "...",
  "max_suggestions": 3
}
```

#### Compare Models
```http
POST /registry/discover/compare
```
Compare multiple models side-by-side.

**Request:**
```json
{
  "model_ids": ["gpt-5-nano", "mistral-small", "llama-3-70b"],
  "criteria": ["cost", "speed", "accuracy", "context_window"]
}
```

#### Get Capability Matrix
```http
GET /registry/discover/capabilities
```
Get matrix of all models and their capabilities.

**Response:**
```json
{
  "capabilities": {
    "vision": ["gpt-4o", "claude-3-opus", "gemini-pro"],
    "audio": ["whisper-3", "gpt-4o"],
    "128k_context": ["claude-3", "gpt-4-turbo"],
    "free_tier": ["llama-3-8b", "mistral-7b"]
  },
  "last_updated": "2024-01-15T10:00:00Z"
}
```

### 5️⃣ Cost & Analytics (`/analytics`)

#### Estimate Cost
```http
POST /analytics/estimate-cost
```
Estimate cost before making a request.

**Request:**
```json
{
  "model_id": "gpt-5-nano",
  "prompt_tokens": 1000,
  "estimated_completion_tokens": 500
}
```

**Response:**
```json
{
  "estimated_cost": {
    "amount": 0.25,
    "currency": "USD",
    "breakdown": {
      "input": 0.05,
      "output": 0.20
    }
  },
  "cheaper_alternatives": [
    {"model": "mistral-small", "cost": 0.10},
    {"model": "llama-3-70b", "cost": 0.00}
  ]
}
```

#### Usage Statistics
```http
GET /analytics/usage
```
Query parameters:
- `start_date`: ISO date
- `end_date`: ISO date
- `group_by`: model|provider|platform|day|hour

**Response:**
```json
{
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-15"
  },
  "total_requests": 15234,
  "total_tokens": 5234567,
  "total_cost": 234.56,
  "cache_hit_rate": 0.34,
  "by_model": [
    {
      "model": "gpt-5-nano",
      "requests": 8234,
      "tokens": 2345678,
      "cost": 123.45
    }
  ]
}
```

### 6️⃣ Cache Management (`/cache`)

#### Get Cache Entry
```http
GET /cache/entries/{cache_id}
```

#### Invalidate Cache Entry
```http
DELETE /cache/entries/{cache_id}
```

### 7️⃣ Health & Status (`/health`)

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "checks": {
    "database": "ok",
    "cache": "ok",
    "providers": {
      "openai": "ok",
      "mistral": "ok",
      "ollama": "unreachable"
    }
  }
}
```

#### Provider Status
```http
GET /health/providers
```

**Response:**
```json
{
  "providers": [
    {
      "provider_id": "openai",
      "status": "operational",
      "latency_ms": 234,
      "last_check": "2024-01-15T12:34:56Z",
      "success_rate_24h": 0.998
    }
  ]
}
```

## 🔄 Response Formats

### Success Response
```json
{
  "success": true,
  "data": {...},
  "metadata": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T12:34:56Z",
    "duration_ms": 234
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "Model 'gpt-6' not found in registry",
    "details": {...}
  },
  "metadata": {...}
}
```