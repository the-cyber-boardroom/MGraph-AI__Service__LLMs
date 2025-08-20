import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str


class Safe_Str__Feature_Id(Safe_Str):                       # Feature identifier for requirements
    max_length = 128
    regex = re.compile(r'[^a-zA-Z0-9\-_:.]')

