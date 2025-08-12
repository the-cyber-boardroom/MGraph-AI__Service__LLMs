from typing                                                  import Dict, Any, Optional
from osbot_utils.type_safe.Type_Safe                         import Type_Safe
from osbot_utils.decorators.methods.cache_on_self            import cache_on_self
from osbot_utils.utils.Env                                   import get_env
from mgraph_ai_service_llms.service.cache.LLM__Cache_Manager import LLM__Cache_Manager
from mgraph_ai_service_llms.service.llms.providers.Provider__OpenRouter import Provider__OpenRouter

ENV_NAME_LLM_CACHE_ENABLED = "LLM_CACHE_ENABLED"            # Environment variable to control cache

class LLM__Service(Type_Safe):              # ain LLM service orchestrator with caching support

    cache_manager: LLM__Cache_Manager = None

    def __init__(self):
        super().__init__()
        # Initialize cache manager based on environment variable
        cache_enabled = get_env(ENV_NAME_LLM_CACHE_ENABLED, "true").lower() == "true"
        self.cache_manager = LLM__Cache_Manager(cache_enabled=cache_enabled)

    @cache_on_self
    def provider(self):
        """Get configured LLM provider"""
        return Provider__OpenRouter()

    def execute_request(self,
                        prompt     : str,
                        model      : str,
                        temperature: float = 0.7,
                        max_tokens : int   = 1000,
                        use_cache  : bool  = True
                       ) -> Dict[str, Any]:
        """Execute LLM request with caching support"""

        # Build the messages for the request
        messages = [
            {
                "role"   : "user",
                "content": prompt
            }
        ]

        # Check cache if enabled
        cache_key = None
        cached_response = None

        if use_cache and self.cache_manager.cache_enabled:
            cache_key = self.cache_manager.generate_cache_key(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            cached_response = self.cache_manager.get_cached_response(cache_key)

            if cached_response:
                # Add cache metadata to response
                cached_response["cache_hit"] = True
                cached_response["cache_key"] = cache_key
                return cached_response

        # Build the request payload for OpenRouter
        llm_payload = {
            "model"      : model,
            "messages"   : messages,
            "temperature": temperature,
            "max_tokens" : max_tokens
        }

        # Execute through provider
        response = self.provider().execute(llm_payload)

        # Format response
        result = {
            "model"       : model,
            "prompt"      : prompt,
            "response"    : response.get("choices", [{}])[0].get("message", {}).get("content", ""),
            "usage"       : response.get("usage", {}),
            "raw_response": response,
            "cache_hit"   : False
        }

        # Cache the response if caching is enabled
        if use_cache and self.cache_manager.cache_enabled and cache_key:
            self.cache_manager.cache_response(cache_key, result)
            result["cache_key"] = cache_key

        return result

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache_manager.get_cache_stats()

    def clear_cache(self) -> bool:
        """Clear the cache"""
        return self.cache_manager.clear_cache()