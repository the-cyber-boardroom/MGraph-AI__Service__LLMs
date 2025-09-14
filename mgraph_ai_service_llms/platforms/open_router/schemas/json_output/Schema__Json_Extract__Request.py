from typing                                                                                     import Dict
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.llm.safe_float.Safe_Float__LLM__Temperature       import Safe_Float__LLM__Temperature
from osbot_utils.type_safe.primitives.domains.llm.safe_str.Safe_Str__LLM__Model_Id              import Safe_Str__LLM__Model_Id
from osbot_utils.type_safe.primitives.domains.llm.safe_uint.Safe_UInt__LLM__Max_Tokens          import Safe_UInt__LLM__Max_Tokens
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Message_Content     import Safe_Str__Message_Content
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers   import Schema__Open_Router__Providers

class Schema__Json_Extract__Request(Type_Safe):                                                          # Request for JSON extraction
    text_content       : Safe_Str__Message_Content                                                       # Text to extract from
    output_schema      : Dict
    model              : Safe_Str__LLM__Model_Id        = None
    provider           : Schema__Open_Router__Providers = None
    temperature        : Safe_Float__LLM__Temperature   = 0.0
    max_tokens         : Safe_UInt__LLM__Max_Tokens     = 5000