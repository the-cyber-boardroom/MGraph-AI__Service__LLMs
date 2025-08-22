# Provider Integration Guide

## 🎯 Overview

This guide details how to integrate new LLM providers into the MGraph-AI__Service__LLMs platform using the Platform → Provider → Model architecture.

## 🏗️ Integration Architecture

### Base Classes Structure

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.decorators import type_safe
from typing import Optional, Dict, Any, Generator

class LLM__Provider__Base(Type_Safe):
    """Base class for all LLM providers"""
    provider_id: str
    api_key: Optional[str] = None
    base_url: str
    timeout: int = 30
    
    @type_safe
    def is_available(self) -> bool:
        """Check if provider is accessible"""
        raise NotImplementedError
    
    @type_safe
    def execute_request(self, request: Schema__LLM_Request) -> Schema__LLM_Response:
        """Execute a request against the provider"""
        raise NotImplementedError
    
    @type_safe
    def execute_stream(self, request: Schema__LLM_Request) -> Generator[str, None, None]:
        """Execute a streaming request"""
        raise NotImplementedError

class LLM__Platform__Engine(Type_Safe):
    """Base class for platform engines"""
    platform_id: str
    provider_id: str
    model_id: str
    
    @type_safe
    def route_request(self, request: Schema__LLM_Request) -> Schema__LLM_Response:
        """Route request through platform"""
        raise NotImplementedError
```

## 📋 Provider Implementation Checklist

### Step 1: Create Provider Class

```python
# File: service/providers/implementations/LLM__YourProvider.py

from osbot_utils.utils.Env import get_env
from service.providers.base.LLM__Provider__Base import LLM__Provider__Base

class LLM__YourProvider(LLM__Provider__Base):
    def __init__(self):
        super().__init__()
        self.provider_id = "your_provider"
        self.base_url = "https://api.yourprovider.com/v1/chat/completions"
        self.api_key = get_env("YOUR_PROVIDER_API_KEY")
    
    def is_available(self) -> bool:
        """Check provider availability"""
        if not self.api_key:
            return False
        
        # Test endpoint reachability
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def execute_request(self, request: Schema__LLM_Request) -> Schema__LLM_Response:
        """Execute standard request"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Convert Type_Safe request to provider format
        payload = self.build_payload(request)
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        return self.parse_response(response.json())
    
    def build_payload(self, request: Schema__LLM_Request) -> Dict:
        """Convert request to provider-specific format"""
        return {
            "model": request.model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
    
    def parse_response(self, raw_response: Dict) -> Schema__LLM_Response:
        """Parse provider response to Type_Safe"""
        return Schema__LLM_Response(
            content=raw_response["choices"][0]["message"]["content"],
            model=raw_response["model"],
            tokens_used=raw_response["usage"]["total_tokens"],
            provider_metadata=raw_response
        )
```

### Step 2: Create Platform Engine

```python
# File: service/engines/Engine__YourProvider.py

from service.engines.base.LLM__Platform__Engine import LLM__Platform__Engine
from service.providers.implementations.LLM__YourProvider import LLM__YourProvider

class Engine__YourProvider(LLM__Platform__Engine):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.provider = LLM__YourProvider()
    
    def execute_request(self):
        """Execute request with this engine"""
        # Add any platform-specific logic
        with self.provider as p:
            p.add_system_messages(self.llm_chat_completion.system_prompts)
            p.add_histories(self.llm_chat_completion.histories)
            p.add_user_message(self.llm_chat_completion.user_prompt)
            p.set_model(self.model_id)
            p.set_stream(self.llm_chat_completion.stream)
            
            if self.llm_chat_completion.stream:
                return p.execute_stream()
            else:
                return p.execute_request()
```

### Step 3: Register in Engine Resolver

```python
# File: service/core/LLM__Engine_Resolver.py

class LLM__Engine_Resolver(Type_Safe):
    @cache_on_self
    def platform_engines(self) -> Dict[str, Type]:
        return {
            'OpenRouter': Engine__OpenRouter,
            'Direct': Engine__Direct,
            'YourProvider': Engine__YourProvider,  # Add your provider
            # ... other providers
        }
    
    def resolve_engine(self, platform: str, provider: str, model: str) -> LLM__Platform__Engine:
        """Resolve the appropriate engine"""
        engine_class = self.platform_engines().get(platform)
        if not engine_class:
            raise ValueError(f"Platform {platform} not supported")
        
        return engine_class(
            platform_id=platform,
            provider_id=provider,
            model_id=model
        )
```

## 🔌 Provider-Specific Features

### Vision Support

```python
class LLM__VisionProvider(LLM__Provider__Base):
    def build_payload_with_images(self, request: Schema__LLM_Request) -> Dict:
        """Handle image inputs"""
        messages = []
        for msg in request.messages:
            if msg.images:
                content = [
                    {"type": "text", "text": msg.content},
                    *[{"type": "image_url", "image_url": {"url": img}} for img in msg.images]
                ]
                messages.append({"role": msg.role, "content": content})
            else:
                messages.append({"role": msg.role, "content": msg.content})
        
        return {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens
        }
```

### Streaming Support

```python
class LLM__StreamingProvider(LLM__Provider__Base):
    def execute_stream(self, request: Schema__LLM_Request) -> Generator[str, None, None]:
        """Stream responses"""
        headers = self.get_headers()
        payload = self.build_payload(request)
        payload["stream"] = True
        
        with requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            stream=True
        ) as response:
            for line in response.iter_lines():
                if line:
                    chunk = self.parse_stream_chunk(line)
                    if chunk:
                        yield chunk
    
    def parse_stream_chunk(self, line: bytes) -> Optional[str]:
        """Parse SSE chunk"""
        if line.startswith(b"data: "):
            data = json.loads(line[6:])
            if data.get("choices"):
                return data["choices"][0]["delta"].get("content", "")
        return None
```

### Function Calling

```python
class LLM__FunctionCallingProvider(LLM__Provider__Base):
    def build_payload_with_functions(self, request: Schema__LLM_Request) -> Dict:
        """Add function definitions"""
        payload = self.build_payload(request)
        
        if request.functions:
            payload["functions"] = [
                {
                    "name": func.name,
                    "description": func.description,
                    "parameters": func.parameters.json_schema()
                }
                for func in request.functions
            ]
            payload["function_call"] = "auto"
        
        return payload
    
    def parse_function_response(self, raw_response: Dict) -> Schema__LLM_Response:
        """Extract function calls from response"""
        response = self.parse_response(raw_response)
        
        if "function_call" in raw_response["choices"][0]["message"]:
            function_call = raw_response["choices"][0]["message"]["function_call"]
            response.function_name = function_call["name"]
            response.function_arguments = json.loads(function_call["arguments"])
        
        return response
```

## 🧪 Testing Provider Integration

### Unit Tests

```python
# File: tests/providers/test_your_provider.py

import pytest
from unittest.mock import patch, Mock
from service.providers.implementations.LLM__YourProvider import LLM__YourProvider

class Test_LLM__YourProvider:
    
    def test_is_available_with_api_key(self):
        with patch.dict('os.environ', {'YOUR_PROVIDER_API_KEY': 'test-key'}):
            provider = LLM__YourProvider()
            with patch('requests.get') as mock_get:
                mock_get.return_value.status_code = 200
                assert provider.is_available() is True
    
    def test_execute_request(self):
        provider = LLM__YourProvider()
        request = Schema__LLM_Request(
            model="your-model",
            messages=[
                Schema__Message(role="user", content="Hello")
            ]
        )
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                "choices": [{
                    "message": {"content": "Hi there!"}
                }],
                "model": "your-model",
                "usage": {"total_tokens": 10}
            }
            
            response = provider.execute_request(request)
            
            assert response.content == "Hi there!"
            assert response.tokens_used == 10
```

### Integration Tests

```python
# File: tests/integration/test_provider_integration.py

class Test_Provider_Integration:
    
    @pytest.mark.integration
    def test_full_request_cycle(self):
        """Test complete request cycle"""
        fast_api = Fast_API()
        fast_api.setup()
        
        with Fast_API_Server(app=fast_api.app()) as server:
            response = server.requests_post(
                '/api/llm/complete',
                data={
                    "prompt": "Hello",
                    "model_id": "your-model",
                    "platform": "your-provider"
                }
            )
            
            assert response.status_code == 200
            assert "response" in response.json()
```

## 📊 Provider Configuration Schema

```yaml
# File: config/providers/your_provider.yaml

provider:
  id: your_provider
  name: Your Provider Name
  description: Description of your provider
  
api:
  base_url: https://api.yourprovider.com/v1
  auth_type: bearer_token
  auth_env_var: YOUR_PROVIDER_API_KEY
  timeout: 30
  max_retries: 3
  
capabilities:
  streaming: true
  vision: false
  audio: false
  function_calling: true
  embeddings: false
  
models:
  - id: your-model-small
    name: Your Model Small
    context_window: 8192
    max_output: 2048
    pricing:
      input: 0.0001
      output: 0.0002
    
  - id: your-model-large
    name: Your Model Large
    context_window: 32768
    max_output: 4096
    pricing:
      input: 0.0005
      output: 0.001

rate_limits:
  requests_per_minute: 100
  tokens_per_minute: 100000
  
error_codes:
  rate_limit: 429
  invalid_auth: 401
  model_not_found: 404
  server_error: 500
```

## 🔄 Provider Lifecycle Management

### Health Monitoring

```python
class Provider__Health_Monitor(Type_Safe):
    
    @type_safe
    def check_provider_health(self, provider_id: str) -> Dict:
        """Check provider health status"""
        provider = self.get_provider(provider_id)
        
        return {
            "provider_id": provider_id,
            "available": provider.is_available(),
            "latency_ms": self.measure_latency(provider),
            "models_available": self.check_models(provider),
            "last_checked": datetime.now()
        }
    
    @type_safe
    def measure_latency(self, provider: LLM__Provider__Base) -> float:
        """Measure provider latency"""
        start = time.time()
        provider.is_available()
        return (time.time() - start) * 1000
```

### Error Handling

```python
class Provider__Error_Handler(Type_Safe):
    
    @type_safe
    def handle_provider_error(self, error: Exception, provider_id: str) -> Schema__LLM_Response:
        """Handle provider-specific errors"""
        
        if isinstance(error, requests.HTTPError):
            if error.response.status_code == 429:
                # Rate limit - try fallback
                return self.try_fallback_provider(provider_id)
            elif error.response.status_code == 401:
                # Auth error
                raise AuthenticationError(f"Invalid API key for {provider_id}")
        
        # Log and re-raise
        self.log_error(error, provider_id)
        raise
```

## 🚀 Best Practices

### 1. Environment Variables
- Always use environment variables for API keys
- Prefix with provider name: `YOUR_PROVIDER_API_KEY`
- Document required variables in README

### 2. Error Handling
- Implement graceful degradation
- Provide meaningful error messages
- Log errors for debugging

### 3. Testing
- Mock external API calls in unit tests
- Use integration tests sparingly
- Test error conditions

### 4. Performance
- Implement connection pooling
- Cache provider availability status
- Use async where possible

### 5. Documentation
- Document provider-specific features
- Include example configurations
- Provide migration guides from direct API usage