import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                       import Safe_Str
from mgraph_ai_service_llms.platforms.open_router.schemas.consts__Open_Router import REGEX__OPEN_ROUTER__MODEL_ID


class Safe_Str__Open_Router__Model_ID(Safe_Str):                               # OpenRouter model identifier
    max_length = 256
    regex      = re.compile(REGEX__OPEN_ROUTER__MODEL_ID)                      # Allow /, -, ., :, _

