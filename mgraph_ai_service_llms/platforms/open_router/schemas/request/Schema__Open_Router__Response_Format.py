from typing                          import Literal
from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Open_Router__Response_Format(Type_Safe):          # Response format configuration
    type : Literal["text", "json_object"] = "text"
