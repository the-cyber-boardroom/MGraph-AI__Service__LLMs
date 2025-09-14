from typing                                                                  import Dict, Any
from osbot_utils.type_safe.Type_Safe                                         import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                          import Safe_Str
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text import Safe_Str__Text


class Schema__Open_Router__Tool__Function(Type_Safe):           # Function definition for OpenRouter tools
    name        : Safe_Str                                      # Function name
    description : Safe_Str__Text                                # Function description
    parameters  : Dict[str, Any]                                # JSON Schema for parameters
