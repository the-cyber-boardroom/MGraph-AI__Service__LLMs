from typing                                                                         import Dict, Any, Optional
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from mgraph_ai_service_llms.service.llms.providers.open_router.Provider__OpenRouter import Provider__OpenRouter


class LLM__Service(Type_Safe):                                      # Main LLM service orchestrator

    @cache_on_self
    def provider(self):                                             # Get configured LLM provider
        return Provider__OpenRouter()

    def execute_request(self,
                        prompt     : str,
                        model      : str,
                        temperature: float = 0.7,
                        max_tokens : int   = 1000,
                       ) -> Dict[str, Any]:                          # Execute LLM request

        # Build the request payload for OpenRouter
        llm_payload = {
            "model"      : model,
            "messages"   : [
                {
                    "role"   : "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens" : max_tokens
        }

        # Execute through provider
        response = self.provider().execute(llm_payload)

        # Format response
        return {
            "model"       : model,
            "prompt"      : prompt,
            "response"    : response.get("choices", [{}])[0].get("message", {}).get("content", ""),
            "usage"       : response.get("usage", {}),
            "raw_response": response
        }