from osbot_utils.type_safe.Type_Safe                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt


# todo: see if the values below should not be UInt (i.e. does it make sense to have negative numbers for prompt or completion tokens

class Schema__Open_Router__Model__Per_Request_Limits(Type_Safe):
    prompt_tokens     : Safe_UInt = None                               # Max prompt tokens per request
    completion_tokens : Safe_UInt = None                               # Max completion tokens per request

