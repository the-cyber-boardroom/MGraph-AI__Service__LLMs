import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                       import Safe_Str
from mgraph_ai_service_llms.platforms.open_router.schemas.consts__Open_Router import REGEX__OPEN_ROUTER__PARAMETER

class Safe_Str__Open_Router__Parameter(Safe_Str):                              # API parameter name
    max_length = 64
    regex      = re.compile(REGEX__OPEN_ROUTER__PARAMETER)                     # Allow _