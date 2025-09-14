from typing                                                                                     import Dict
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                           import Safe_Float
from osbot_utils.type_safe.primitives.core.Safe_UInt                                            import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash              import Safe_Str__Hash
from osbot_utils.type_safe.primitives.domains.llm.safe_str.Safe_Str__LLM__Model_Id              import Safe_Str__LLM__Model_Id
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers   import Schema__Open_Router__Providers

class Schema__Json_Extract__Response(Type_Safe):                                                         # Response for JSON extraction
    cache_id           : Safe_Str__Hash                 = None
    duration           : Safe_Float                     = None
    json_data          : Dict                           = None
    model              : Safe_Str__LLM__Model_Id        = None
    provider           : Schema__Open_Router__Providers = None
    tokens             : Safe_UInt                      = None
