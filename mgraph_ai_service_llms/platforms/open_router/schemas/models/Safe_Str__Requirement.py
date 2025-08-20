import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str


class Safe_Str__Requirement(Safe_Str):                         # Bearer token for authorization - allows typical token characters
    max_length = 512
    regex      = re.compile(r'[^a-zA-Z0-9-_]')              # Allow Base64-like chars, dots and spaces
