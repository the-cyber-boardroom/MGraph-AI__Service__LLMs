from typing                                             import Optional, List, Literal
from osbot_utils.type_safe.Type_Safe                    import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str


class Schema__Open_Router__Provider_Preferences(Type_Safe):                 # Provider-specific preferences and settings"""
    allow_fallbacks            : bool                     = True            # Allow fallback to other providers
    require_parameters         : List[str]                = None            # Required parameters support
    data_collection            : Literal["allow", "deny"] = None            # Data collection preference
    ignore_providers           : List[Safe_Str          ] = None            # Providers to exclude
    order                      : List[Safe_Str          ] = None            # Provider preference order
