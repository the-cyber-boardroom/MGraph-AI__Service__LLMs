from osbot_utils.type_safe.Type_Safe                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_float.Safe_Float import Safe_Float

class Schema__Open_Router__Model__Pricing(Type_Safe):
    prompt             : Safe_Float                                             # Cost per token for prompts
    completion         : Safe_Float                                             # Cost per token for completions
    request            : Safe_Float                                             # Cost per request
    image              : Safe_Float                                             # Cost for image processing
    audio              : Safe_Float                                             # Cost for audio processing
    web_search         : Safe_Float                                             # Cost for web search
    internal_reasoning : Safe_Float                                             # Cost for internal reasoning

