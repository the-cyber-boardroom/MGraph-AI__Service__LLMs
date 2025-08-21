from typing                                                                                   import Dict, Any, Optional
from osbot_utils.helpers.duration.decorators.capture_duration                                 import capture_duration
from osbot_utils.type_safe.Type_Safe                                                          import Type_Safe
from osbot_utils.decorators.methods.cache_on_self                                             import cache_on_self
from mgraph_ai_service_llms.service.llms.providers.open_router.Provider__OpenRouter           import Provider__OpenRouter
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers import Schema__Open_Router__Providers

class LLM__Service(Type_Safe):

    @cache_on_self
    def provider(self):
        return Provider__OpenRouter()

    def execute_request(self, prompt        : str,
                              model         : str,
                              temperature   : float = 0.7,
                              max_tokens    : int = 1000,
                              provider      : Schema__Open_Router__Providers = None
                         ) -> Dict[str, Any]:

        
        # Build the request payload
        llm_payload = { "model"         : model                     ,
                        "messages"      : [ { "role": "user"        ,
                                              "content": prompt } ] ,
                        "temperature"   : temperature               ,
                        "max_tokens"    : max_tokens                }

        # Execute through provider with optional provider routing
        with capture_duration() as duration__llm_execution:
            response = self.provider().execute( llm_payload, provider=provider)

        # Format response
        result = { "model"       : model                           ,
                   "provider"    : provider                        ,
                   "duration"    : duration__llm_execution.seconds ,
                   "prompt"      : prompt                          ,
                   "response"    : response.get("choices", [{}])[0].get("message", {}).get("content", ""),
                   "usage"       : response.get("usage", {})      ,
                   "raw_response": response
        }
            
        return result