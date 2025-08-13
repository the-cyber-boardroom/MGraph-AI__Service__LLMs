# MGraph-AI Service LLMs Documentation

## 🎯 Overview

MGraph-AI Service LLMs is a production-ready, Type-Safe LLM service that provides a unified interface to multiple LLM platforms, providers, and models while maintaining strong typing, comprehensive caching, and enterprise-grade monitoring.

## 🏗️ Core Architecture

The service follows a **Platform → Provider → Model** hierarchy that reflects the reality of the LLM ecosystem:

```
Platform (OpenRouter, Direct, Local)
    └── Provider (OpenAI, Mistral AI, Meta, Google)
            └── Model (GPT-5-nano, Mistral-Small, Llama-3)
```

### Key Design Principles
- **Open Router Model**: Support multiple pathways to access the same model
- **Type-Safe Throughout**: Leveraging OSBot-Utils Type_Safe for runtime validation
- **API-First Design**: Every capability exposed through REST APIs
- **Universal Caching**: All LLM requests cached with S3 backend
- **Dynamic Model Registry**: API-driven model management

## 📚 Documentation Structure

### 🏛️ Architecture Documentation
Core architectural documentation explaining the system design and patterns:

- **[Core Principles and Architecture](./architecture/mgraph-ai_service_llms__core-principles-and-architecture.md)** - Foundation principles and high-level design
- **[API Endpoints Specification](./architecture/api-endpoints-specification.md)** - Complete REST API specification
- **[Model Registry Design](./architecture/model-registry-design.md)** - Dynamic model management system
- **[Provider Integration Guide](./architecture/provider-integration-guide.md)** - How to add new LLM providers
- **[Caching Strategy](./architecture/caching-strategy.md)** - Multi-layer caching architecture

### 🔧 Implementation Documentation
Detailed implementation guides and references:

- **[Implementation Context and Prerequisites](./architecture/implementation/implementation-context-and-prerequisites.md)** - What you need before starting
- **[Code Patterns and Examples](./architecture/implementation/code-patterns-and-examples.md)** - Common patterns and code examples
- **[Complete Schemas Reference](./architecture/implementation/complete-schemas-reference.md)** - All Type-Safe schemas used in the system

### 👩‍💻 Development Documentation
Guidelines and setup instructions for developers:

#### Setup Guides
- **[Complete Setup Guide](./dev/setup/compete-guide-to-setup-new-repo.md)** - Full repository setup instructions
- **[Repository Setup](./dev/setup/repo-setup-guide.md)** - Initial repository configuration
- **[Documentation Setup](./dev/setup/docs-setup-guide.md)** - How to maintain documentation
- **[Architecture Setup](./dev/setup/architecture.md)** - Setting up the development architecture

#### Non-Functional Requirements
- **[Python Code Formatting Guidelines](./dev/non-functional-requirements/python-code-formatting-guidelines.md)** - Code style and formatting standards
- **[Version 1.0.0 Requirements](./dev/non-functional-requirements/version-1_0_0/README.md)** - Target requirements for v1.0.0
- **[Development Decisions](./dev/non-functional-requirements/version-1_0_0/why-not-use-github-templates.md)** - Architectural decisions explained

### 📋 Change Log
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history and release notes

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- AWS CLI configured (for deployment)
- Docker (for LocalStack testing)
- Environment variables configured

### Local Development
```bash
# Clone the repository
git clone https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs.git
cd MGraph-AI__Service__LLMs

# Install dependencies
pip install -r requirements-test.txt
pip install -e .

# Set environment variables
export FAST_API__AUTH__API_KEY__NAME="x-api-key"
export FAST_API__AUTH__API_KEY__VALUE="your-secret-key"
export OPEN_ROUTER__API_KEY="your-openrouter-key"  # If using OpenRouter

# Run locally
./scripts/run-locally.sh
```

## 🎯 Key Features

### Multiple Input/Output Patterns
The service supports various interaction patterns:

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Text → Text** | Simple string in/out | Basic queries |
| **Text → Schema** | String to Type_Safe object | Structured extraction |
| **Schema → Text** | Type_Safe object to string | Template generation |
| **Schema → Schema** | Type_Safe to Type_Safe | Data transformation |
| **Batch → Batch** | List processing | Bulk operations |

### Model Registry
Dynamic, API-driven model management:
- CRUD operations for platforms, providers, and models
- Cost tracking and optimization
- Capability matrix (vision, audio, streaming, etc.)
- Automatic fallback chains

### Caching System
Multi-layer caching architecture:
- Memory cache (L1) - ~100 entries
- Local file cache (L2) - ~1000 entries  
- S3 cache (L3) - Unlimited
- Temporal organization for easy management
- Cost tracking and ROI analysis

## 🔌 Supported Providers

### Currently Implemented
- **OpenRouter** - Multiple providers through single API
- **OpenAI** - Direct access with audio support
- **Groq** - Fast inference with free tier
- **Mistral** - Open models with function calling
- **Ollama** - Local deployment option

### Coming Soon
- **Anthropic** - Claude models
- **Google** - Gemini models
- **AWS Bedrock** - Enterprise integration
- **Azure OpenAI** - Enterprise OpenAI

## 📊 API Examples

### Simple Text Completion
```bash
curl -X POST "http://localhost:8000/api/llm/complete" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "prompt": "What is quantum computing?",
    "model_id": "gpt-5-nano",
    "platform": "openrouter"
  }'
```

### Structured Extraction
```bash
curl -X POST "http://localhost:8000/api/llm/extract" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "text": "John Doe, 30 years old, lives in New York",
    "schema": "Person"
  }'
```

### Model Search
```bash
curl -X POST "http://localhost:8000/api/registry/models/search" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "capabilities": ["vision", "128k_context"],
    "max_input_cost": 0.001
  }'
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mgraph_ai_service_llms

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

## 🚢 Deployment

The service supports multiple deployment targets:

### AWS Lambda
- Optimized for serverless with Mangum
- Auto-scaling and pay-per-use
- Cold start optimization

### Docker Container
- For Kubernetes or ECS deployment
- Includes health checks and monitoring

### Local Development
- FastAPI with hot reload
- LocalStack for AWS service mocking
- Built-in Swagger documentation

## 📈 Monitoring & Analytics

### Built-in Metrics
- Request/response tracking
- Cache hit rates and cost savings
- Model usage statistics
- Performance metrics by provider

### Integration Points
- CloudWatch (AWS)
- Prometheus endpoints
- Custom webhooks for alerts

## 🔒 Security

- **API Key Authentication** - Required for all endpoints
- **Type-Safe Validation** - Runtime type checking
- **Environment-based Configuration** - No hardcoded secrets
- **Request Sanitization** - Input validation at all boundaries
- **Audit Logging** - Complete request/response tracking

## 🤝 Contributing

See our [Contributing Guidelines](../CONTRIBUTING.md) for details on:
- Code style and formatting
- Testing requirements
- Pull request process
- Documentation standards

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs/discussions)
- **Documentation**: This documentation and inline code documentation

## 🗺️ Roadmap

### Phase 1: Core Infrastructure ✅
- Platform Engine architecture
- Model Registry with S3 backend
- Type-Safe schemas
- Base REST API structure

### Phase 2: Provider Integration (In Progress)
- OpenRouter integration
- Direct provider support
- Streaming capabilities
- Error handling and fallbacks

### Phase 3: Advanced Features (Planned)
- Schema input/output endpoints
- Batch processing APIs
- Cost tracking and analytics
- Admin UI for model management

### Phase 4: Production Hardening (Future)
- Rate limiting and quotas
- Advanced monitoring
- Performance optimization
- Multi-region support

---

Created and maintained by [The Cyber Boardroom](https://github.com/the-cyber-boardroom) team