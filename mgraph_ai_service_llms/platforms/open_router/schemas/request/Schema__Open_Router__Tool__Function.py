from typing                                                                  import Dict, Any
from osbot_utils.type_safe.Type_Safe                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id            import Safe_Id


class Schema__Open_Router__Tool__Function(Type_Safe):           # Function definition for OpenRouter tools
    name        : Safe_Id                                       # Function name                     # todo: see if we need a better regex here: Safe_Id uses r'[^a-zA-Z0-9_-]'
    description : Safe_Str__Text                                # Function description
    parameters  : Dict[str, Any]                                # JSON Schema for parameters
