from mgraph_ai_service_llms import package_name

SERVICE_NAME                             = package_name
FAST_API__TITLE                          = "MGraph-AI LLM Service"
FAST_API__DESCRIPTION                    = "Production-ready LLM service with multiple providers"
LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS = ['osbot-fast-api-serverless==v1.2.0']

# LLM Configuration (todo: see if we need this)
#LLM__DEFAULT_MODEL                       = "mistralai/mistral-small-3.2-24b-instruct:free"
#LLM__CACHE__ENABLED                      = True
#LLM__CACHE__TTL_SECONDS                  = 3600  # 1 hour