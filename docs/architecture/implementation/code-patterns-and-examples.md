# Code Patterns and Examples

## 🎯 Overview

This document provides concrete code examples and patterns that should be followed when implementing the MGraph-AI__Service__LLMs system.

## 📋 Complete Service Implementation Example

### Main FastAPI Service

```python
# File: fast_api/Service__Fast_API.py

import logging
from osbot_fast_api.api.Fast_API import Fast_API
from mgraph_ai_service_llms.config import FAST_API__TITLE
from mgraph_ai_service_llms.fast_api.routes.Routes__LLMs import Routes__LLMs
from mgraph_ai_service_llms.fast_api.routes.Routes__Registry import Routes__Registry
from mgraph_ai_service_llms.fast_api.routes.Routes__Cache import Routes__Cache
from mgraph_ai_service_llms.fast_api.routes.Routes__Admin import Routes__Admin
from mgraph_ai_service_llms.utils.LocalStack__Setup import LocalStack__Setup
from mgraph_ai_service_llms.utils.Version import version__mgraph_ai_service_llms

class Service__Fast_API(Fast_API):
    
    def fast_api__title(self):
        return FAST_API__TITLE
    
    def setup(self):
        self.setup_localstack()
        super().setup()
        self.setup_fast_api_title_and_version()
        return self
    
    def setup_fast_api_title_and_version(self):
        app = self.app()
        app.title = self.fast_api__title()
        app.version = version__mgraph_ai_service_llms
        return self
    
    def setup_localstack(self):
        with LocalStack__Setup() as _:
            if _.is_localstack_enabled():
                logger = logging.getLogger("uvicorn")
                logger.warning('LocalStack enabled')
                _.setup()
    
    def setup_routes(self):
        self.add_routes(Routes__LLMs)
        self.add_routes(Routes__Registry)
        self.add_routes(Routes__Cache)
        self.add_routes(Routes__Admin)
```

### Route Implementation Example

```python
# File: fast_api/routes/Routes__LLMs.py

from typing import Dict, Any
from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes
from osbot_utils.type_safe.decorators import type_safe
from mgraph_ai_service_llms.service.schemas.Schema__LLM_Request import Schema__LLM_Request
from mgraph_ai_service_llms.service.schemas.Schema__LLM_Response import Schema__LLM_Response
from mgraph_ai_service_llms.service.core.Service__LLM import Service__LLM

TAG__ROUTES_LLMS = 'llms'
ROUTES_PATHS__LLMS = [
    f'/{TAG__ROUTES_LLMS}/complete',
    f'/{TAG__ROUTES_LLMS}/extract',
    f'/{TAG__ROUTES_LLMS}/transform',
    f'/{TAG__ROUTES_LLMS}/batch'
]

class Routes__LLMs(Fast_API_Routes):
    tag: str = TAG__ROUTES_LLMS
    service_llm: Service__LLM = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service_llm = Service__LLM().setup()
    
    @type_safe
    def complete(self, prompt: str, 
                      model_id: str = "gpt-5-nano",
                      platform: str = None,
                      temperature: float = 0.7,
                      max_tokens: int = None) -> Dict[str, Any]:
        """Execute basic text completion"""
        
        request = Schema__LLM_Request(
            model_id=model_id,
            platform=platform,
            messages=[
                Schema__LLM_Message(role="user", content=prompt)
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        response = self.service_llm.execute_request(request)
        
        return {
            "response": response.choices[0].message.content,
            "model_used": response.model,
            "platform_used": response.platform_used,
            "tokens": response.usage.json(),
            "cost": response.cost.json(),
            "cache_hit": response.cache_hit,
            "request_id": response.response_id
        }
    
    @type_safe
    def extract(self, text: str,
                     schema_name: str,
                     model_id: str = None) -> Dict[str, Any]:
        """Extract structured data from text"""
        
        result = self.service_llm.extract_to_schema(
            text=text,
            schema_name=schema_name,
            model_id=model_id
        )
        
        return result.json()
    
    @type_safe
    def transform(self, input_schema: str,
                       output_schema: str,
                       data: Dict[str, Any],
                       model_id: str = None) -> Dict[str, Any]:
        """Transform data from one schema to another"""
        
        result = self.service_llm.transform_schema(
            input_schema=input_schema,
            output_schema=output_schema,
            data=data,
            model_id=model_id
        )
        
        return result.json()
    
    def setup_routes(self):
        self.add_route_post(self.complete)
        self.add_route_post(self.extract)
        self.add_route_post(self.transform)
```

## 🔧 Provider Implementation Pattern

### Base Provider Class

```python
# File: service/providers/base/LLM__Provider__Base.py

from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.decorators import type_safe
from typing import Optional, Dict, Any, Generator
from abc import abstractmethod

class LLM__Provider__Base(Type_Safe):
    provider_id: str
    api_key: Optional[str] = None
    base_url: str
    timeout: int = 30
    
    @type_safe
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is accessible"""
        raise NotImplementedError
    
    @type_safe
    @abstractmethod
    def build_request(self, request: Schema__LLM_Request) -> Dict[str, Any]:
        """Convert Type_Safe request to provider format"""
        raise NotImplementedError
    
    @type_safe
    @abstractmethod
    def parse_response(self, raw_response: Dict[str, Any]) -> Schema__LLM_Response:
        """Parse provider response to Type_Safe"""
        raise NotImplementedError
    
    @type_safe
    def execute_request(self, request: Schema__LLM_Request) -> Schema__LLM_Response:
        """Execute a standard request"""
        if not self.is_available():
            raise ValueError(f"Provider {self.provider_id} is not available")
        
        payload = self.build_request(request)
        raw_response = self.send_request(payload)
        return self.parse_response(raw_response)
    
    @type_safe
    def execute_stream(self, request: Schema__LLM_Request) -> Generator[str, None, None]:
        """Execute a streaming request"""
        if not self.is_available():
            raise ValueError(f"Provider {self.provider_id} is not available")
        
        payload = self.build_request(request)
        payload["stream"] = True
        
        for chunk in self.send_stream_request(payload):
            yield chunk
```

### Concrete Provider Implementation

```python
# File: service/providers/implementations/LLM__OpenRouter.py

import requests
from osbot_utils.utils.Env import get_env
from osbot_utils.utils.Json import json_parse
from mgraph_ai_service_llms.service.providers.base.LLM__Provider__Base import LLM__Provider__Base

class LLM__OpenRouter(LLM__Provider__Base):
    
    def __init__(self):
        super().__init__()
        self.provider_id = "openrouter"
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = get_env("OPEN_ROUTER_API_KEY")
        self.http_referer = "https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs"
    
    @type_safe
    def is_available(self) -> bool:
        """Check OpenRouter availability"""
        if not self.api_key:
            return False
        
        try:
            # Test with a minimal request
            headers = self.get_headers()
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    @type_safe
    def get_headers(self) -> Dict[str, str]:
        """Get OpenRouter-specific headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.http_referer,
            "X-Title": "MGraph-AI LLM Service"
        }
    
    @type_safe
    def build_request(self, request: Schema__LLM_Request) -> Dict[str, Any]:
        """Build OpenRouter request payload"""
        
        # Convert messages
        messages = []
        for msg in request.messages:
            message = {
                "role": msg.role,
                "content": msg.content
            }
            
            # Handle images if present
            if msg.images:
                content = [{"type": "text", "text": msg.content}]
                for img in msg.images:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": img}
                    })
                message["content"] = content
            
            messages.append(message)
        
        # Build payload
        payload = {
            "model": request.model_id,
            "messages": messages,
            "temperature": request.temperature,
            "stream": request.stream
        }
        
        # Add optional parameters
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        if request.top_p:
            payload["top_p"] = request.top_p
        if request.functions:
            payload["functions"] = [
                func.json() for func in request.functions
            ]
        
        return payload
    
    @type_safe
    def parse_response(self, raw_response: Dict[str, Any]) -> Schema__LLM_Response:
        """Parse OpenRouter response"""
        
        # Extract choices
        choices = []
        for choice in raw_response.get("choices", []):
            choices.append(Schema__LLM_Choice(
                index=choice["index"],
                message=Schema__LLM_Message(
                    role=choice["message"]["role"],
                    content=choice["message"]["content"]
                ),
                finish_reason=choice.get("finish_reason", "stop")
            ))
        
        # Extract usage
        usage_data = raw_response.get("usage", {})
        usage = Schema__LLM_Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        )
        
        # Calculate cost (OpenRouter provides this)
        cost = Schema__LLM_Cost(
            input_cost=0.0,  # Calculate based on model pricing
            output_cost=0.0,
            total_cost=0.0
        )
        
        return Schema__LLM_Response(
            choices=choices,
            model=raw_response.get("model"),
            usage=usage,
            cost=cost,
            response_id=raw_response.get("id", ""),
            created_at=datetime.now(),
            platform_used="openrouter",
            provider_used=self.extract_provider(raw_response.get("model")),
            latency_ms=0.0,  # Set by caller
            raw_response=raw_response
        )
```

## 🎯 Engine Pattern Implementation

### Platform Engine

```python
# File: service/engines/Engine__OpenRouter.py

from mgraph_ai_service_llms.service.core.engine.LLM__Platform_Engine import LLM__Platform_Engine
from mgraph_ai_service_llms.service.providers.implementations.LLM__OpenRouter import LLM__OpenRouter

class Engine__OpenRouter(LLM__Platform_Engine):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.provider = LLM__OpenRouter()
    
    @type_safe
    def execute_request(self, request: Schema__LLM_Request) -> Schema__LLM_Response:
        """Execute request through OpenRouter"""
        
        # Set platform-specific configurations
        if self.model_id in self.get_free_models():
            request.model_id = f"{request.model_id}:free"
        
        # Execute through provider
        if request.stream:
            return self.execute_stream(request)
        else:
            with capture_duration() as duration:
                response = self.provider.execute_request(request)
                response.latency_ms = duration.milliseconds
            
            return response
    
    @type_safe
    def execute_stream(self, request: Schema__LLM_Request) -> Generator[str, None, None]:
        """Stream response through OpenRouter"""
        
        complete_response = ""
        for chunk in self.provider.execute_stream(request):
            complete_response += chunk
            yield chunk
        
        # Store complete response for caching
        self.cache_streamed_response(request, complete_response)
    
    @type_safe
    def get_free_models(self) -> List[str]:
        """Get list of free models on OpenRouter"""
        return [
            "meta-llama/llama-3-8b-instruct",
            "mistralai/mistral-7b-instruct",
            "google/gemma-7b"
        ]
```

### Engine Resolver

```python
# File: service/core/engine/LLM__Engine_Resolver.py

from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from typing import Dict, Type

class LLM__Engine_Resolver(Type_Safe):
    
    @cache_on_self
    def platform_engines(self) -> Dict[str, Type]:
        """Registry of platform engines"""
        return {
            'openrouter': Engine__OpenRouter,
            'direct': Engine__Direct,
            'groq': Engine__Groq,
            'ollama': Engine__Ollama,
            'mistral': Engine__Mistral,
            'sambanova': Engine__SambaNova
        }
    
    @type_safe
    def resolve_engine(self, 
                      platform: str,
                      provider: str,
                      model: str) -> LLM__Platform_Engine:
        """Resolve the appropriate engine for a request"""
        
        # Get engine class
        engine_class = self.platform_engines().get(platform.lower())
        if not engine_class:
            raise ValueError(f"Platform '{platform}' not supported")
        
        # Instantiate engine
        engine = engine_class(
            platform_id=platform,
            provider_id=provider,
            model_id=model
        )
        
        # Validate engine is available
        if not engine.is_available():
            # Try fallback
            fallback = self.get_fallback_engine(model)
            if fallback:
                return fallback
            raise ValueError(f"Platform '{platform}' is not available and no fallback found")
        
        return engine
    
    @type_safe
    def get_fallback_engine(self, model: str) -> Optional[LLM__Platform_Engine]:
        """Get fallback engine for a model"""
        
        # Try to find alternative platforms for the model
        registry = Service__Model_Registry()
        routes = registry.get_routes_for_model(model)
        
        for route in sorted(routes, key=lambda r: r.priority):
            if route.status == "active":
                try:
                    return self.resolve_engine(
                        platform=route.platform_id,
                        provider=route.provider_id,
                        model=model
                    )
                except:
                    continue
        
        return None
```

## 💾 Cache Implementation Pattern

### Cache Key Generator

```python
# File: service/cache/Cache__Key_Generator.py

from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.utils.Json import json_md5
from typing import List, Dict, Any

class Cache__Key_Generator(Type_Safe):
    
    @type_safe
    def generate_key(self, request: Schema__LLM_Request) -> str:
        """Generate deterministic cache key"""
        
        # Normalize request for consistent hashing
        normalized = self.normalize_request(request)
        
        # Generate hash
        content_hash = json_md5(normalized)[:16]
        
        # Create readable key
        model_short = request.model_id.replace('/', '_')[:20]
        cache_key = f"{model_short}_{content_hash}"
        
        return cache_key
    
    @type_safe
    def normalize_request(self, request: Schema__LLM_Request) -> Dict[str, Any]:
        """Normalize request for caching"""
        
        # Extract cacheable parts
        normalized = {
            "model": request.model_id.lower().strip(),
            "messages": self.normalize_messages(request.messages),
            "temperature": self.normalize_temperature(request.temperature),
        }
        
        # Only include non-default values
        if request.max_tokens:
            normalized["max_tokens"] = request.max_tokens
        if request.functions:
            normalized["functions"] = [
                func.name for func in request.functions
            ]
        
        return normalized
    
    @type_safe
    def normalize_messages(self, messages: List[Schema__LLM_Message]) -> List[Dict]:
        """Normalize messages for consistent hashing"""
        
        normalized = []
        for msg in messages:
            # Normalize whitespace and case
            content = ' '.join(msg.content.split()).lower()
            
            normalized.append({
                "role": msg.role.lower(),
                "content": content,
                "has_images": bool(msg.images)
            })
        
        return normalized
    
    @type_safe
    def normalize_temperature(self, temp: float) -> float:
        """Normalize temperature for caching"""
        
        # Round to 1 decimal place
        # Temperatures within 0.05 are considered equivalent
        return round(temp, 1)
```

### Cache Manager

```python
# File: service/cache/Service__Cache_Manager.py

from osbot_utils.type_safe.Type_Safe import Type_Safe
from mgraph_ai_service_llms.service.cache.LLM__Cache import LLM__Cache

class Service__Cache_Manager(Type_Safe):
    cache: LLM__Cache
    key_generator: Cache__Key_Generator
    
    def __init__(self):
        super().__init__()
        self.cache = LLM__Cache().setup()
        self.key_generator = Cache__Key_Generator()
    
    @type_safe
    async def get_or_execute(self,
                            request: Schema__LLM_Request,
                            executor: Callable) -> Schema__LLM_Response:
        """Get from cache or execute and cache"""
        
        # Check if caching is enabled
        if not request.use_cache:
            return await executor(request)
        
        # Generate cache key
        cache_key = self.key_generator.generate_key(request)
        
        # Check cache
        cached = await self.get_from_cache(cache_key)
        if cached:
            cached.cache_hit = True
            await self.update_hit_stats(cache_key)
            return cached
        
        # Execute request
        response = await executor(request)
        
        # Cache response
        await self.cache_response(cache_key, request, response)
        
        return response
    
    @type_safe
    async def get_from_cache(self, cache_key: str) -> Optional[Schema__LLM_Response]:
        """Get response from cache"""
        
        # Try to get from cache
        cache_path = self.get_cache_path(cache_key)
        cached_data = self.cache.json__load(cache_path)
        
        if cached_data:
            # Deserialize
            cache_entry = Schema__Cache_Entry.from_json(cached_data)
            
            # Check if expired
            if self.is_expired(cache_entry):
                return None
            
            return cache_entry.response
        
        return None
    
    @type_safe
    def get_cache_path(self, cache_key: str) -> str:
        """Generate S3 path for cache entry"""
        
        now = datetime.now()
        model = cache_key.split('_')[0]
        
        path = f"llm-cache/{model}/{now.year}/{now.month:02d}/{now.day:02d}/{now.hour:02d}/{cache_key}.json"
        
        return path
```

## 🧪 Testing Pattern

```python
# File: tests/service/test_llm_service.py

import pytest
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server
from mgraph_ai_service_llms.fast_api.Service__Fast_API import Service__Fast_API

class Test_LLM_Service:
    
    @classmethod
    def setUpClass(cls):
        cls.fast_api = Service__Fast_API()
        cls.fast_api.setup()
    
    def test_complete_endpoint(self):
        with Fast_API_Server(app=self.fast_api.app()) as server:
            response = server.requests_post(
                '/api/llms/complete',
                data={
                    'prompt': 'What is 2+2?',
                    'model_id': 'gpt-5-nano',
                    'temperature': 0.0
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert 'response' in data
            assert 'model_used' in data
            assert 'cost' in data
            assert '4' in data['response'].lower()
    
    def test_caching(self):
        """Test that identical requests hit cache"""
        
        with Fast_API_Server(app=self.fast_api.app()) as server:
            # First request - cache miss
            response1 = server.requests_post(
                '/api/llms/complete',
                data={'prompt': 'Test prompt', 'model_id': 'gpt-5-nano'}
            )
            assert response1.json()['cache_hit'] == False
            
            # Second request - cache hit
            response2 = server.requests_post(
                '/api/llms/complete',
                data={'prompt': 'Test prompt', 'model_id': 'gpt-5-nano'}
            )
            assert response2.json()['cache_hit'] == True
            
            # Responses should be identical
            assert response1.json()['response'] == response2.json()['response']
```

## 📝 Key Implementation Rules

1. **Always use Type_Safe classes**, never Pydantic BaseModel
2. **Use @type_safe decorator** on all public methods
3. **Follow the naming convention** for routes (method_name → /method-name)
4. **Cache all LLM requests** using deterministic keys
5. **Use environment variables** for all configuration
6. **Implement proper error handling** with meaningful messages
7. **Add comprehensive logging** for debugging
8. **Write tests for all endpoints** using Fast_API_Server
9. **Document all Type_Safe schemas** with clear field descriptions
10. **Don't async/await** unless there isn't another way (specially since FastAPI doesn't support it well)