from typing                                                     import Optional, Dict, Any
from osbot_fast_api.api.Fast_API_Routes                         import Fast_API_Routes
from mgraph_ai_service_llms.service.llms.LLM__Service           import LLM__Service
from mgraph_ai_service_llms.service.schemas.Schema__LLM__Models import Schema__LLM__Models

TAG__ROUTES_LLMS                  = 'llms'
ROUTES_PATHS__LLMS                = [ f'/{TAG__ROUTES_LLMS}/models'  ,
                                      f'/{TAG__ROUTES_LLMS}/complete']

class Routes__LLMs(Fast_API_Routes):
    tag = 'llms'
    llm_service: LLM__Service = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm_service = LLM__Service()

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

    def setup_routes(self):
        self.add_route_get (self.models )
        self.add_route_post(self.complete)