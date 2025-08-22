import re
from osbot_utils.type_safe.primitives.safe_str.Enum__Safe_Str__Regex_Mode import Enum__Safe_Str__Regex_Mode
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                   import Safe_Str


class Safe_Str__Request_Id(Safe_Str):                   # Request tracking ID - alphanumeric with hyphens and underscores
    max_length  = 256
    regex       = re.compile(r'[^a-zA-Z0-9\-_]')
    regex_mode  = Enum__Safe_Str__Regex_Mode.REPLACE
