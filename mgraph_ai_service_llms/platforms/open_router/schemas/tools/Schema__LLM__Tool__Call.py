from typing                                                                     import Dict, Any
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id

# todo: review the use of Any in the class type below

class Schema__LLM__Tool__Call(Type_Safe):                                                                     # Single tool call from LLM
    name      : Safe_Str                                                                                      # Tool/function name called
    arguments : Dict[str, Any]                                                                                # Arguments for the tool call
    id        : Safe_Str__Id = None                                                                     # Tool call ID from provider