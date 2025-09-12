import re
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode import Enum__Safe_Str__Regex_Mode
from osbot_utils.type_safe.primitives.core.Safe_Str                   import Safe_Str


class Safe_Str__Provider_Id(Safe_Str):                                              # Provider identifier - lowercase with hyphens"""
    max_length = 64
    regex = re.compile(r'[^a-z0-9\-_]')
    regex_mode = Enum__Safe_Str__Regex_Mode.REPLACE
