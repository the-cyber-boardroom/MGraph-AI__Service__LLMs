from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                           import Safe_Float
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text


class Schema__Entity(Type_Safe):                                                # Single entity with metadata
    name        : Safe_Str
    type        : Safe_Str
    confidence  : Safe_Float
    description : Safe_Str__Text