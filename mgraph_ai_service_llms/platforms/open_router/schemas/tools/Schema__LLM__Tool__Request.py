from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.llm.safe_float.Safe_Float__LLM__Temperature                   import Safe_Float__LLM__Temperature
from osbot_utils.type_safe.primitives.domains.llm.safe_str.Safe_Str__LLM__Message__System                   import Safe_Str__LLM__Message__System
from osbot_utils.type_safe.primitives.domains.llm.safe_str.Safe_Str__LLM__Prompt                            import Safe_Str__LLM__Prompt
from osbot_utils.type_safe.primitives.domains.llm.safe_uint.Safe_UInt__LLM__Max_Tokens                      import Safe_UInt__LLM__Max_Tokens
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Definition               import Schema__LLM__Tool__Definition
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers               import Schema__Open_Router__Providers
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Supported_Models        import Schema__Open_Router__Supported_Models

DEFAULT__LLM__TOOL__MODEL = Schema__Open_Router__Supported_Models.Open_AI__GPT_OSS_20b

class Schema__LLM__Tool__Request(Type_Safe):                                                       # Request for LLM completion with tool/function support
    user_prompt      : Safe_Str__LLM__Prompt                                                       # User prompt that may trigger tool use
    system_prompt    : Safe_Str__LLM__Message__System               = None                         # System prompt for context
    tool_definition  : Schema__LLM__Tool__Definition                                               # Tool schema from calling service
    model            : Schema__Open_Router__Supported_Models         = DEFAULT__LLM__TOOL__MODEL
    provider         : Schema__Open_Router__Providers                = None                        # provider routing
    temperature      : Safe_Float__LLM__Temperature                  = 0.0                         # Lower temp for tool use
    max_tokens       : Safe_UInt__LLM__Max_Tokens                    = 5000                        # Enough for tool calls
    force_tool_use   : bool                                          = True                        # Force LLM to use the tool



