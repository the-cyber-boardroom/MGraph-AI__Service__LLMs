from mgraph_ai_service_llms                                                                          import package_name
from osbot_utils.helpers.safe_str.Safe_Str__File__Path                                               import Safe_Str__File__Path
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Supported_Models import Schema__Open_Router__Supported_Models

SERVICE_NAME                             = package_name
FAST_API__TITLE                          = "MGraph-AI LLM Service"
FAST_API__DESCRIPTION                    = "Production-ready LLM service with multiple providers"
LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS = ['osbot-fast-api-serverless==v1.2.0']

# LLM Configuration (todo: see if we need this)
#LLM__DEFAULT_MODEL                       = "mistralai/mistral-small-3.2-24b-instruct:free"
#LLM__CACHE__ENABLED                      = True
#LLM__CACHE__TTL_SECONDS                  = 3600  # 1 hour


LLM__CACHE__DEFAULT__ROOT_FOLDER = Safe_Str__File__Path('llm-cache/')
LLM__CACHE__BUCKET_NAME__PREFIX  = 'service-llm-cache'
LLM__CACHE__BUCKET_NAME__SUFFIX  = 'data'
LLM__MODEL_TO_USE__DEFAULT       = Schema__Open_Router__Supported_Models.Open_AI__GPT_5__Nano