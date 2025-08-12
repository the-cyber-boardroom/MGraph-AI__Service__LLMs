from osbot_utils.helpers.safe_str.Safe_Str__File__Path import Safe_Str__File__Path

from mgraph_ai_service_llms import package_name

SERVICE_NAME                             = package_name
FAST_API__TITLE                          = "MGraph-AI LLM Service"
FAST_API__DESCRIPTION                    = "Production-ready LLM service with multiple providers and caching"
LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS = ['osbot-fast-api-serverless==v1.5.0']

# LLM Cache Configuration
LLM__CACHE__ENABLED                      = True
LLM__CACHE__TTL_SECONDS                  = 3600  # 1 hour (for future TTL implementation)       # todo: see if we acually use this
LLM__CACHE__BUCKET_PREFIX                = 'mgraph-ai-llms'
LLM__CACHE__BUCKET_SUFFIX                = 'cache'
LLM__CACHE__ROOT_FOLDER                  = 'llm-service-cache/'
LLM__CACHE__DEFAULT__ROOT_FOLDER         = Safe_Str__File__Path('llm-service-cache/')
LLM__CACHE__BUCKET_NAME__PREFIX          = 'mgraph-ai-llms'
LLM__CACHE__BUCKET_NAME__SUFFIX          = 'cache'


# LocalStack Configuration (for development)
LOCALSTACK__ENABLED                      = False  # Set to True for local development
LOCALSTACK__ENDPOINT_URL                 = 'http://localhost:4566'
LOCALSTACK__REGION_NAME                  = 'us-east-1'


ENV_VAR__LOCALSTACK_ENABLED              = 'LOCALSTACK_ENABLED'