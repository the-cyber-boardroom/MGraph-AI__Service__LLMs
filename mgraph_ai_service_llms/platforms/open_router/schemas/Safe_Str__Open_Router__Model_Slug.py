import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                       import Safe_Str
from mgraph_ai_service_llms.platforms.open_router.schemas.consts__Open_Router import REGEX__OPEN_ROUTER__MODEL_SLUG

class Safe_Str__Open_Router__Model_Slug(Safe_Str):                             # URL-safe model slug
    max_length = 256
    regex      = re.compile(REGEX__OPEN_ROUTER__MODEL_SLUG)                    # Allow /, -, ., _