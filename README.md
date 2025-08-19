# MGraph-AI Service LLMs

[![Current Release](https://img.shields.io/badge/release-v0.6.15-blue)](https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs/releases)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688)](https://fastapi.tiangolo.com/)
[![Type-Safe](https://img.shields.io/badge/Type--Safe-✓-brightgreen)](https://github.com/owasp-sbot/OSBot-Utils)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange)](https://aws.amazon.com/lambda/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![CI Pipeline - DEV](https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs/actions/workflows/ci-pipeline__dev.yml/badge.svg)](https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs/actions)

A Type-Safe LLM service that provides a unified interface to multiple LLM platforms, providers, and models. Built on the **Platform → Provider → Model** hierarchy with comprehensive caching, cost tracking, and enterprise-grade monitoring.

## 🎯 Overview

MGraph-AI__Service__LLMs consolidates access to multiple LLM providers through a single, consistent API. It implements an "Open Router" model where the same model can be accessed through multiple pathways (direct to provider, via platforms, or locally), with automatic fallback.

### Key Features

- **🔄 Multi-Route Access**: Same model accessible via multiple platforms (OpenRouter, Direct, Local)
- **🏗️ Platform → Provider → Model Architecture**: Clean three-tier hierarchy reflecting the LLM ecosystem
- **💾 Universal Caching**: All LLM requests cached with S3 backend and temporal organization
- **📊 Dynamic Model Registry**: API-driven model management with cost tracking
- **🔒 Type-Safe Throughout**: Using OSBot-Utils Type_Safe for runtime validation
- **🔄 Multiple I/O Patterns**: Text↔Schema transformations in all combinations
- **🚀 Production Ready**: Built-in monitoring, error handling, and AWS Lambda support

## 📚 Documentation

- [Core Principles and Architecture](docs/architecture/core-principles.md)
- [Model Registry Design](docs/architecture/model-registry-design.md)
- [API Endpoints Specification](docs/api/api-endpoints-spec.md)
- [Provider Integration Guide](docs/guides/provider-integration-guide.md)
- [Caching Strategy](docs/architecture/caching-strategy.md)
- [Implementation Context](docs/dev/implementation-context.md)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs.git
cd MGraph-AI__Service__LLMs

# Install dependencies
pip install -r requirements-test.txt
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

```bash
# Provider API Keys
OPEN_ROUTER_API_KEY=or-...
OPEN_AI__API_KEY=sk-...
GROQ_API_KEY=gsk_...
MISTRAL_API_KEY=...

# Service Configuration
FAST_API__AUTH__API_KEY__NAME=X-API-Key
FAST_API__AUTH__API_KEY__VALUE=your-service-api-key

# LocalStack (for development)
LOCALSTACK_ENABLED=true  # Set to false for production

# Cache Configuration
LLM__CACHE__BUCKET_NAME__PREFIX=service-llm-cache
LLM__CACHE__BUCKET_NAME__SUFFIX=data
```

### Running Locally

```bash
# Start the service
./scripts/run-locally.sh
# or
uvicorn mgraph_ai_service_llms.fast_api.lambda_handler:app --reload --host 0.0.0.0 --port 10011

# Access the API documentation
open http://localhost:10011/docs
```

## 🔌 API Usage Examples

### Simple Text Completion

```python
import requests

headers = {"X-API-Key": "your-service-api-key"}
base_url = "http://localhost:10011"

# Basic completion
response = requests.post(
    f"{base_url}/api/llms/complete",
    headers=headers,
    json={
        "prompt": "What is quantum computing?",
        "model_id": "gpt-5-nano",
        "platform": "openrouter",  
        "temperature": 0.7
    }
)

result = response.json()
print(f"Response: {result['response']}")
print(f"Cost: ${result['cost']['total']:.4f}")
print(f"Cache hit: {result['cache_hit']}")
```

### Text to Schema Extraction

```python
# Extract structured data from text
response = requests.post(
    f"{base_url}/api/llms/extract",
    headers=headers,
    json={
        "text": "John Doe, 30 years old, lives in New York",
        "schema": "Person",  # Reference to registered schema
        "model_id": "gpt-4o-mini"
    }
)

data = response.json()
# Returns: {"name": "John Doe", "age": 30, "city": "New York"}
```

### Schema to Schema Transformation

```python
# Transform data between schemas
response = requests.post(
    f"{base_url}/api/llms/transform",
    headers=headers,
    json={
        "input_schema": "RawData",
        "output_schema": "ProcessedData",
        "data": {"raw_text": "Revenue: $1M, Costs: $600K"},
        "model_id": "gpt-5-mini"
    }
)

result = response.json()
# Returns: {"revenue": 1000000, "costs": 600000, "profit": 400000, "margin": 0.4}
```

### Batch Processing

```python
# Process multiple requests in parallel
response = requests.post(
    f"{base_url}/api/llms/batch",
    headers=headers,
    json={
        "requests": [
            {"id": "1", "prompt": "Summarize: ...", "max_tokens": 100},
            {"id": "2", "prompt": "Translate: ...", "max_tokens": 200},
            {"id": "3", "prompt": "Analyze: ...", "max_tokens": 150}
        ],
        "model_id": "gpt-5-nano",
        "parallel": True,
        "max_concurrent": 3
    }
)
```

## 🏗️ Architecture

### Platform → Provider → Model Hierarchy

```
Platform (OpenRouter, Direct, Local)
    └── Provider (OpenAI, Mistral AI, Meta, Google)
            └── Model (GPT-5-nano, Mistral-Small, Llama-3)
```

### Supported Platforms & Providers

| Platform | Providers | Models | Status |
|----------|-----------|--------|--------|
| **OpenRouter** | 15+ providers | 100+ models | ✅ Active |
| **Direct** | OpenAI, Mistral, Groq | Provider models | ✅ Active |
| **Local** | Ollama | Open models | ✅ Active |
| **AWS Bedrock** | Amazon, Anthropic | Bedrock models | 🚧 Coming Soon |

### Model Registry

The service includes a dynamic, API-driven model registry:

```python
# Search for models with specific capabilities
GET /api/registry/models/search
{
    "capabilities": ["vision", "128k_context"],
    "max_input_cost": 0.001,
    "tags": ["free"]
}

# Get model details with available routes
GET /api/registry/models/gpt-5-nano

# Update model pricing
PATCH /api/registry/models/gpt-5-nano/pricing
```

## 💾 Caching Strategy

### Cache Organization

```
s3://mgraph-ai-llm-cache/
├── llm-cache/
│   ├── {model}/
│   │   ├── {year}/{month}/{day}/{hour}/
│   │   │   └── {cache_id}.json
├── cache-index/
│   └── cache_index.json
```

## 📊 Cost Management

### Cost Estimation

```python
# Compare costs across models
POST /api/cost/estimate
{
    "prompt": "Your prompt here...",
    "estimated_output_tokens": 500,
    "models": ["gpt-5-nano", "mistral-small", "llama-3-8b"]
}
```

### Usage Analytics

```python
# Get usage statistics
GET /api/cost/usage?start_date=2024-11-01&end_date=2024-11-30

# Returns detailed breakdown by model, platform, and cost savings
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests (requires LocalStack)
pytest tests/integration/

# Run with coverage
pytest --cov=mgraph_ai_service_llms

# Test specific endpoint
pytest tests/unit/fast_api/routes/test_Routes__LLMs.py
```

## 🚀 Deployment

### AWS Lambda

```bash
# Deploy to development
pytest tests/deploy_aws/test_Deploy__Service__to__dev.py

# Deploy to QA
pytest tests/deploy_aws/test_Deploy__Service__to__qa.py

# Production deployment via GitHub Actions
```

### Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "mgraph_ai_service_llms.fast_api.lambda_handler:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🛠️ Development

### Adding a New Provider

1. Create provider implementation:
```python
# service/providers/implementations/LLM__YourProvider.py
class LLM__YourProvider(LLM__Provider__Base):
    def is_available(self) -> bool
    def build_request(self, request: Schema__LLM_Request) -> Dict
    def parse_response(self, raw: Dict) -> Schema__LLM_Response
```

2. Create platform engine:
```python
# service/engines/Engine__YourProvider.py
class Engine__YourProvider(LLM__Platform_Engine):
    def execute_request(self, request: Schema__LLM_Request)
```

3. Register in engine resolver:
```python
# service/core/LLM__Engine_Resolver.py
def platform_engines(self):
    return {
        'your_provider': Engine__YourProvider,
        # ...
    }
```

### Project Structure

```
mgraph_ai_service_llms/
├── fast_api/
│   ├── Service__Fast_API.py       # Main FastAPI setup
│   └── routes/
│       ├── Routes__LLMs.py        # LLM endpoints
│       ├── Routes__Registry.py    # Model registry
│       └── Routes__Cache.py       # Cache management
├── service/
│   ├── core/
│   │   └── engine/                # Platform engines
│   ├── providers/                 # Provider implementations
│   ├── registry/                  # Model registry
│   ├── cache/                     # Caching system
│   └── schemas/                   # Type-Safe schemas
└── utils/
    ├── LocalStack__Setup.py       # Development setup
    └── Version.py                 # Version management
```

## 📈 Monitoring

### Health Checks

```python
GET /api/admin/health

# Returns service health and provider status
{
    "status": "healthy",
    "providers": {
        "openai": "up",
        "openrouter": "up",
        "groq": "up",
        "ollama": "not_configured"
    }
}
```

### Metrics

- Request rate and latency
- Cache hit rate and cost savings
- Provider availability and performance
- Model usage distribution

## 🔒 Security

- **API Key Authentication**: All endpoints require authentication
- **Environment Variables**: Never commit secrets
- **Request Validation**: Type-Safe validation on all inputs
- **Rate Limiting**: Configurable per API key
- **Audit Logging**: All requests logged with user context

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Related Projects

- [OSBot-Utils](https://github.com/owasp-sbot/OSBot-Utils) - Type-Safe framework
- [OSBot-Fast-API](https://github.com/owasp-sbot/OSBot-Fast-API) - FastAPI utilities
- [OSBot-AWS](https://github.com/owasp-sbot/OSBot-AWS) - AWS integrations

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Type safety via [OSBot-Utils](https://github.com/owasp-sbot/OSBot-Utils)
- Deployed on [AWS Lambda](https://aws.amazon.com/lambda/) and any other Cloud Provider or Data Center (online or offline) 

## 📞 Support

- 🐛 Issues: [GitHub Issues](https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs/discussions)
- 📖 Documentation: [Docs](https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs/tree/main/docs) folder

---

Created and maintained by [The Cyber Boardroom](https://github.com/the-cyber-boardroom) team