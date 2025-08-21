from typing                                                                                      import Optional, Dict, Any
from osbot_fast_api.api.routes.Fast_API__Routes                                                  import Fast_API__Routes
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Tag                                       import Safe_Str__Fast_API__Route__Tag
from osbot_utils.type_safe.Type_Safe                                                             import Type_Safe
from mgraph_ai_service_llms.platforms.open_router.service.Service__LLM__Simple                   import Service__LLM__Simple, HIGH_THROUGHPUT_MODELS
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers    import Schema__Open_Router__Providers

TAG__ROUTES_LLM_SIMPLE   = 'llm-simple'
ROUTES_PATHS__LLM_SIMPLE = [f'/{TAG__ROUTES_LLM_SIMPLE}/complete']

class User_Prompt_Simple(Type_Safe):                                                                # Simple LLM completion
    user_prompt   : str                            = "Hello, what is your name and model"
    system_prompt : Optional[str]                  = "Reply in CamelCase"
    model         : str                            = "gpt-oss-120b"
    provider      : Schema__Open_Router__Providers = Schema__Open_Router__Providers.GROQ

class Routes__LLM__Simple(Fast_API__Routes):
    tag            : Safe_Str__Fast_API__Route__Tag = TAG__ROUTES_LLM_SIMPLE
    service_simple : Service__LLM__Simple           = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service_simple = Service__LLM__Simple()

    def complete(self, user_prompt_simple: User_Prompt_Simple) -> Dict[str, Any]:
        return self.service_simple.execute_completion(user_prompt   = user_prompt_simple.user_prompt   ,
                                                      system_prompt = user_prompt_simple.system_prompt ,
                                                      model_key     = user_prompt_simple.model         ,
                                                      provider_name = user_prompt_simple.provider      )

    def models(self) -> Dict[str, Any]:                                                                 # List available models
        return { "available_models" : HIGH_THROUGHPUT_MODELS }

    def setup_routes(self):
        self.add_route_post(self.complete )
        self.add_route_get (self.models   )