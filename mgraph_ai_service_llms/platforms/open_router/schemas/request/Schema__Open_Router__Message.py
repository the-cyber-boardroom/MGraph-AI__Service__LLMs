from typing                                                                                 import Optional, Literal
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                     import Safe_Str
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Message_Content import Safe_Str__Message_Content


class Schema__Open_Router__Message(Type_Safe):                    # Chat message structure
    role         : Literal["assistant", "system", "user", "tool"] # only allow "system", "user", "assistant", "tool"
    content      : Safe_Str__Message_Content                      # Message content
    name         : Optional[Safe_Str] = None                      # For tool messages
    tool_call_id : Optional[Safe_Str] = None                      # For tool responses
