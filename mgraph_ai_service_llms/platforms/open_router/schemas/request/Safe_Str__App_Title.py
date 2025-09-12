import re
from osbot_utils.type_safe.primitives.core.Safe_Str                         import Safe_Str
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode import Enum__Safe_Str__Regex_Mode


class Safe_Str__App_Title(Safe_Str):                        # Application title - allows spaces and common punctuation
    max_length = 256
    regex = re.compile(r'[^a-zA-Z0-9 _\-\.\,\'\"]')
    regex_mode = Enum__Safe_Str__Regex_Mode.REPLACE
