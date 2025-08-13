from typing                                                                                          import Dict, Any
from osbot_fast_api.api.Fast_API_Routes                                                              import Fast_API_Routes
from osbot_utils.helpers.llms.schemas.Safe_Str__LLM__Model_Name import Safe_Str__LLM__Model_Name
from osbot_utils.utils.Env                                                                           import load_dotenv
from mgraph_ai_service_llms.config                                                                   import LLM__MODEL_TO_USE__DEFAULT, TEST_DATA__SIMPLE_TEXT
from mgraph_ai_service_llms.service.llms.LLM__Execute_Request                                        import LLM__Execute_Request
from mgraph_ai_service_llms.service.llms.LLM__Service                                                import LLM__Service
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Supported_Models import Schema__Open_Router__Supported_Models
from mgraph_ai_service_llms.service.schemas.Schema__LLM__Models                                      import Schema__LLM__Models

TAG__ROUTES_LLMS                  = 'llms'
ROUTES_PATHS__LLMS                = [ f'/{TAG__ROUTES_LLMS}/models'                    ,
                                      f'/{TAG__ROUTES_LLMS}/complete'                  ,
                                      f'/{TAG__ROUTES_LLMS}/extract-facts'             ,
                                      f'/{TAG__ROUTES_LLMS}/extract-facts-request-hash']

class Routes__LLMs(Fast_API_Routes):
    tag                     : str                    = TAG__ROUTES_LLMS
    llm_service             : LLM__Service           = None
    llm_execute_request     : LLM__Execute_Request   = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()
        self.llm_service = LLM__Service()
        self.llm_execute_request = LLM__Execute_Request().setup()

    def models(self) -> Dict[str, Any]:                             # List available models
        return {
            "models": [
                {
                    "id"      : model.value,
                    "name"    : model.name,
                    "is_free" : model.is_free,
                    "provider": model.provider
                }
                for model in Schema__LLM__Models
            ]
        }

    def complete(self, prompt     : str,
                       model      : Schema__LLM__Models = Schema__LLM__Models.MISTRAL_SMALL_FREE,
                       temperature: float               = 0.7,
                       max_tokens : int                 = 1000
                  ) -> Dict[str, Any]:                               # Execute completion request
        result = self.llm_service.execute_request(prompt      = prompt,
                                                   model       = model.value,
                                                   temperature = temperature,
                                                   max_tokens  = max_tokens)
        return result

    def extract_facts(self, text_content: str                                   = TEST_DATA__SIMPLE_TEXT,
                            model       : Schema__Open_Router__Supported_Models = LLM__MODEL_TO_USE__DEFAULT
                       ) -> Dict[str, Any]:                                 # Extract facts from text content"""

        # Execute fact extraction with caching
        result = self.llm_execute_request.extract_facts(text_content=text_content, model_to_use=model)
        return result

    def extract_facts_request_hash(self, text_content: str                                   = TEST_DATA__SIMPLE_TEXT,
                                         model       : Schema__Open_Router__Supported_Models = LLM__MODEL_TO_USE__DEFAULT
                                    ) -> dict:
        result = self.llm_execute_request.extract_facts__request_hash(text_content=text_content, model_to_use=Safe_Str__LLM__Model_Name(model))
        return { 'text_content' : text_content,
                 'model'        : model       ,
                 'result'       : result      }

    def setup_routes(self):
        self.add_route_get (self.models         )
        self.add_route_post(self.complete       )
        self.add_route_post(self.extract_facts  )
        self.add_route_post(self.extract_facts_request_hash)