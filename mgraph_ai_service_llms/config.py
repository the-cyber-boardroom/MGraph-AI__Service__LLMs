from mgraph_ai_service_llms                                                                          import package_name
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path                                               import Safe_Str__File__Path
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Supported_Models import Schema__Open_Router__Supported_Models

SERVICE_NAME                             = package_name
FAST_API__TITLE                          = "MGraph-AI LLM Service"
FAST_API__DESCRIPTION                    = "LLM service with multiple providers"

LOCALSTACK__ENDPOINT_URL                 = 'http://localhost:4566'
LOCALSTACK__REGION_NAME                  = 'us-east-1'


LLM__CACHE__DEFAULT__ROOT_FOLDER = Safe_Str__File__Path('llm-cache/')
LLM__CACHE__BUCKET_NAME__PREFIX  = 'service-llm-cache'
LLM__CACHE__BUCKET_NAME__SUFFIX  = 'data'
LLM__MODEL_TO_USE__DEFAULT       = Schema__Open_Router__Supported_Models.Open_AI__GPT_5__Nano

ENV_VAR__LOCALSTACK_ENABLED      = 'LOCALSTACK_ENABLED'

TEST_DATA__SIMPLE_TEXT = "This is a text about GenAI and MCP"