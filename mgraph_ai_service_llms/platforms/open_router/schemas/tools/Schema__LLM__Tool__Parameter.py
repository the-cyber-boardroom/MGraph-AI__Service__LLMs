from typing                                                                  import List, Any, Dict
from osbot_utils.type_safe.Type_Safe                                         import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                          import Safe_Str
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text import Safe_Str__Text


# todo: review the use of Any in the class type below

class Schema__LLM__Tool__Parameter(Type_Safe):            # Single parameter definition for LLM tools
    name        : Safe_Str                                # Parameter name
    type        : Safe_Str                                # JSON Schema type: "string", "number", "boolean", etc.
    description : Safe_Str__Text = None                   # Parameter description
    required    : bool           = True                   # Whether parameter is required
    enum        : List[Safe_Str] = None                   # Allowed values for enum types
    default     : Any            = None                   # Default value if not required
    properties  : Dict[str, Any] = None                   # For nested object types
    items       : Dict[str, Any] = None                   # For array types