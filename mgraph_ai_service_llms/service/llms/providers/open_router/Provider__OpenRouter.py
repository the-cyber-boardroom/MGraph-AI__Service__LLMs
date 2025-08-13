from typing                                                                                     import Dict, Any, Optional
from urllib.error                                                                               import HTTPError
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.utils.Http                                                                     import POST_json
from osbot_utils.utils.Env                                                                      import get_env
from osbot_utils.utils.Json                                                                     import str_to_json
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers   import Schema__Open_Router__Providers

ENV_NAME_OPEN_ROUTER__API_KEY = "OPEN_ROUTER__API_KEY"

class Provider__OpenRouter(Type_Safe):
    api_url     : str = "https://openrouter.ai/api/v1/chat/completions"
    api_key_name: str = ENV_NAME_OPEN_ROUTER__API_KEY
    http_referer: str = "https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs"

    def api_key(self) -> str:
        return get_env(self.api_key_name)

    def execute(self,
                llm_payload          : Dict[str, Any],
                provider             : Schema__Open_Router__Providers = None
           ) -> Dict[str, Any]:

        headers = { "Authorization"     : f"Bearer {self.api_key()}",
                    "Content-Type"      : "application/json"        ,
                    "HTTP-Referer"      : self.http_referer         ,
                    "X-Title"           : "MGraph-AI LLM Service"   ,
                    "X-Include-Provider": "true"                    }                              # default to ask OpenRouter to provide this info


        if provider and provider != Schema__Open_Router__Providers.AUTO:                           # Add provider-specific routing if specified
            headers["X-Provider"] = provider.value


        try:
            response = POST_json(self.api_url, headers=headers, data=llm_payload)

            # # Extract provider info if available
            # if include_provider_info and "provider" in response:
            #     response["_provider_info"] = {
            #         "requested": provider.value if provider else "auto",
            #         "actual": response.get("provider", "unknown")
            #     }

            return response
        except HTTPError as error:
            error_message = str_to_json(error.file.read().decode("utf-8"))
            raise ValueError(error_message)