from typing                                    import Optional
from osbot_utils.type_safe.Type_Safe           import Type_Safe
from osbot_utils.type_safe.primitives.safe_int import Safe_Int

# todo: see if the values below should not be UInt (i.e. does it make sense to have negative numbers for prompt or completion tokens

class Schema__Open_Router__Model__Per_Request_Limits(Type_Safe):
    prompt_tokens     : Optional[Safe_Int] = None                               # Max prompt tokens per request
    completion_tokens : Optional[Safe_Int] = None                               # Max completion tokens per request

