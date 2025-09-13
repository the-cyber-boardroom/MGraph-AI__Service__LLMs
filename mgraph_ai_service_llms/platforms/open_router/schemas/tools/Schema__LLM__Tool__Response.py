from typing                                                                             import List
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text            import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash      import Safe_Str__Hash
from osbot_utils.type_safe.primitives.domains.llm.safe_str.Safe_Str__LLM__Model_Id      import Safe_Str__LLM__Model_Id
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Provider_Id import Safe_Str__Provider_Id
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Call import Schema__LLM__Tool__Call


class Schema__LLM__Tool__Response(Type_Safe):                                                       # Response from LLM with tool calls
    tool_calls       : List[Schema__LLM__Tool__Call]                                                # Tool invocations from LLM
    response_content : Safe_Str__Text                     = None                                    # Any text response from LLM
    requires_action  : bool                               = False                                   # True if tools need execution
    cache_id         : Safe_Str__Hash                     = None                                    # Cache identifier
    model_used       : Safe_Str__LLM__Model_Id                                                      # Actual model used
    provider_used    : Safe_Str__Provider_Id              = None                                    # Actual provider used