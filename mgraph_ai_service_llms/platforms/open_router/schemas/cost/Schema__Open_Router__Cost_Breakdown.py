
from typing                                                                               import  Dict
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.type_safe.primitives.safe_float.Safe_Float                               import Safe_Float
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                   import Safe_Str
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_ID import Safe_Str__Open_Router__Model_ID


class Schema__Open_Router__Cost_Breakdown(Type_Safe):               # Detailed cost breakdown for a request
    prompt_tokens        : int                                              # Number of prompt tokens
    completion_tokens    : int                                          # Number of completion tokens
    total_tokens         : int                                          # Total tokens used
    prompt_cost          : Safe_Float                                   # Cost for prompt tokens
    completion_cost      : Safe_Float                                   # Cost for completion tokens
    cache_read_cost      : Safe_Float = None                            # Cost for cache reads (if applicable)
    cache_write_cost     : Safe_Float = None                            # Cost for cache writes (if applicable)
    image_cost           : Safe_Float = None                            # Cost for image processing
    audio_cost           : Safe_Float = None                            # Cost for audio processing
    web_search_cost      : Safe_Float = None                            # Cost for web search
    reasoning_cost       : Safe_Float = None                            # Cost for internal reasoning
    request_cost         : Safe_Float = None                            # Per-request cost (if applicable)
    total_cost           : Safe_Float                                   # Total cost in USD
    cost_per_1k_tokens   : Safe_Float                                   # Average cost per 1000 tokens
    model_id             : Safe_Str__Open_Router__Model_ID              # Model used
    provider             : Safe_Str = None                              # Provider used (if known)

    def to_display_dict(self) -> Dict[str, str]:
        """Convert to human-readable display format"""
        return {
            "prompt_tokens"     : str(self.prompt_tokens)                          ,
            "completion_tokens" : str(self.completion_tokens)                      ,
            "total_tokens"      : str(self.total_tokens)                           ,
            "prompt_cost"       : f"${self.prompt_cost:.6f}"                       ,
            "completion_cost"   : f"${self.completion_cost:.6f}"                   ,
            "total_cost"        : f"${self.total_cost:.6f}"                        ,
            "cost_per_1k"       : f"${self.cost_per_1k_tokens:.6f}"                ,
            "model"             : str(self.model_id)                               ,
            "provider"          : str(self.provider) if self.provider else "auto"  ,
        }