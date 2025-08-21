from typing                                                                                                  import Dict, Any, Optional
import time
from osbot_utils.type_safe.Type_Safe                                                                         import Type_Safe
from osbot_utils.utils.Dev import pprint

from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                               import Service__Open_Router
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Provider_Preferences  import Schema__Open_Router__Provider_Preferences
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers                import Schema__Open_Router__Providers

HIGH_THROUGHPUT_MODELS = { "gpt-oss-120b"  : "openai/gpt-oss-120b"  ,
                           "gpt-oss-20b"   : "openai/gpt-oss-20b"   ,
                           "gpt-5-nano"    : "openai/gpt-5-nano"    ,
                           "gpt-5-mini"    : "openai/gpt-5-mini"    ,
                           "gemini-2"      : "google/gemini-2.0-flash-lite-001"}


class Service__LLM__Simple(Type_Safe):
    open_router : Service__Open_Router = None

    def __init__(self):
        super().__init__()
        self.open_router = Service__Open_Router()

    def execute_completion(self, user_prompt   : str                                             ,      # Execute LLM completion with provider routing
                                system_prompt : Optional[str]                            = None ,
                                model_key     : str                                      = "gpt-oss-120b",
                                provider_name : Optional[Schema__Open_Router__Providers] = None
                          ) -> Dict[str, Any]:

        model_id = HIGH_THROUGHPUT_MODELS.get(model_key)
        if not model_id:
            raise ValueError(f"Invalid model key: {model_key}. Valid options: {list(HIGH_THROUGHPUT_MODELS.keys())}")

        start_time = time.perf_counter()

        # Use provider name directly - Service__Open_Router expects a string
        provider_value = provider_name.value if provider_name else None

        response = self.open_router.chat_completion(
            prompt        = user_prompt    ,
            model         = model_id       ,
            system_prompt = system_prompt  ,
            temperature   = 0              ,
            max_tokens    = 20000          ,
            provider      = provider_value ,
            max_cost      = 0.5            )

        duration = time.perf_counter() - start_time

        #pprint(response)
        response_text   = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        actual_provider = response.get("provider", provider_value or "auto")

        return { "duration_seconds" : round(duration, 3)   ,
                 "model_used"       : model_id             ,
                 "provider_used"    : actual_provider      ,
                 "response_text"    : response_text        }

    # def execute_completion_with_preferences(self, user_prompt          : str                                             ,      # Execute with full provider preferences
    #                                               system_prompt        : Optional[str]                            = None ,
    #                                               model_key            : str                                      = "gpt-oss-120b",
    #                                               provider_preferences : Optional[Schema__Open_Router__Provider_Preferences] = None
    #                                        ) -> Dict[str, Any]:
    #
    #     model_id = HIGH_THROUGHPUT_MODELS.get(model_key)
    #     if not model_id:
    #         raise ValueError(f"Invalid model key: {model_key}. Valid options: {list(HIGH_THROUGHPUT_MODELS.keys())}")
    #
    #     start_time = time.perf_counter()
    #
    #     # Extract provider from preferences if provided
    #     provider_value = None
    #     if provider_preferences and provider_preferences.order:
    #         provider_value = str(provider_preferences.order[0])
    #
    #     response = self.open_router.chat_completion(
    #         prompt        = user_prompt    ,
    #         model         = model_id       ,
    #         system_prompt = system_prompt  ,
    #         temperature   = 0.7            ,
    #         max_tokens    = 500            ,
    #         provider      = provider_value ,
    #         max_cost      = 0.5            )
    #
    #     duration = time.perf_counter() - start_time
    #
    #     response_text   = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    #     actual_provider = response.get("provider", provider_value or "auto")
    #
    #     return { "duration_seconds"     : round(duration, 3)                                                ,
    #              "model_used"           : model_id                                                         ,
    #              "provider_requested"   : provider_value                                                   ,
    #              "provider_used"        : actual_provider                                                  ,
    #              "provider_preferences" : provider_preferences.json() if provider_preferences else None    ,
    #              "response_text"        : response_text                                                    }