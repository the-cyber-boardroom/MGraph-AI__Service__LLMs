import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                       import Safe_Str
from mgraph_ai_service_llms.platforms.open_router.schemas.consts__Open_Router import REGEX__OPEN_ROUTER__TOKENIZER

class Safe_Str__Open_Router__Tokenizer(Safe_Str):                              # Tokenizer type identifier
    max_length = 64
    regex      = re.compile(REGEX__OPEN_ROUTER__TOKENIZER)                     # Allow -, _, space
