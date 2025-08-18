from typing                                             import Optional
from osbot_utils.type_safe.Type_Safe                    import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Safe_Int import Safe_Int


class Schema__Open_Router__Model__Top_Provider(Type_Safe):
    context_length         : Safe_Int           = None                          # Maximum context length
    max_completion_tokens  : Optional[Safe_Int] = None                          # Maximum completion tokens
    is_moderated           : bool                                               # Whether the model is moderated
