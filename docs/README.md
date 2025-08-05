# MGraph-AI Service LLMs Documentation

## Overview

MGraph-AI Service LLMs will be a production-ready FastAPI microservice that provides Large Language Model (BASE) capabilities through a secure, type-safe API. 

## Architecture

The service follows a clean architecture pattern with clear separation of concerns:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   API Layer     │     │  Service Layer  │     │ Infrastructure  │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ FastAPI Routes  │────▶│ Business Logic  │────▶│ AWS Lambda      │
│ Authentication  │     │ Type Safety     │     │ OSBot-AWS       │
│ OpenAPI Docs    │     │ Data Validation │     │ External APIs   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Key Features

### 1. Type Safety
- Built on OSBot-Utils type safety framework
- Runtime type checking and validation
- Prevents injection attacks at the type level

### 2. Multi-Stage Deployment
- Development environment with auto-deployment on push to `dev` branch
- QA environment with auto-deployment on push to `main` branch
- Production environment with manual deployment trigger

### 3. AWS Lambda Optimization
- Cold start optimization with dependency pre-loading
- Efficient memory usage
- Automatic scaling

### 4. API Security
- API key authentication required for all endpoints
- Environment-based configuration
- Secure secret management

## Getting Started

### Prerequisites
- Python 3.12+
- AWS CLI configured (for deployment)
- Docker (for LocalStack testing)

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

# Run locally
./scripts/run-locally.sh
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mgraph_ai_service_llms

# Run specific test file
pytest tests/unit/fast_api/test_Service__Fast_API__client.py
```

## API Endpoints

### Health Check
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health status with component information

### Service Information
- `GET /info/version` - Get current service version
- `GET /info/status` - Get service status and environment information

## Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `FAST_API__AUTH__API_KEY__NAME` | Header name for API key | Yes |
| `FAST_API__AUTH__API_KEY__VALUE` | API key value | Yes |
| `AWS_REGION` | AWS region (triggers Lambda mode) | No |
| `DEBUG` | Enable debug logging | No |

## Deployment

### CI/CD Pipeline
The service uses GitHub Actions for continuous deployment:

1. **Development** (`dev` branch)
   - Runs unit tests
   - Deploys to AWS Lambda dev environment
   - Increments minor version

2. **QA** (`main` branch)
   - Runs full test suite
   - Deploys to AWS Lambda QA environment
   - Increments major version

3. **Production** (manual trigger)
   - Runs full test suite
   - Requires manual approval
   - Deploys to AWS Lambda production environment

### AWS Lambda Configuration
```yaml
Runtime: python3.12
Handler: mgraph_ai_service_llms.fast_api.lambda_handler.run
MemorySize: 512
Timeout: 30
Environment:
  Variables:
    FAST_API__AUTH__API_KEY__NAME: "x-api-key"
    FAST_API__AUTH__API_KEY__VALUE: "${ssm:/api-key/value}"
```

## Development Guidelines

### Adding New Features
1. Create feature branch from `dev`
2. Add new route in `fast_api/routes/`
3. Add service logic in `service/`
4. Write comprehensive tests
5. Update documentation
6. Submit pull request to `dev`

### Code Style
- Use type annotations for all parameters
- Follow existing naming conventions
- Write descriptive docstrings
- Ensure 100% test coverage for new code

### Security Considerations
- Always validate inputs using type-safe classes
- Never commit secrets or API keys
- Use environment variables for configuration
- Implement proper error handling

## Support

- **Issues**: [GitHub Issues](https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs/discussions)
- **Documentation**: This document and inline code documentation

---

Created and maintained by [The Cyber Boardroom](https://github.com/the-cyber-boardroom) team