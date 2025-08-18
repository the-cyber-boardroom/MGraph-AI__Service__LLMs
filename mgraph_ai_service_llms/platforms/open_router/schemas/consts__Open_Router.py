from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url import Safe_Str__Url

URL__OPEN_ROUTER__API            : Safe_Str__Url = Safe_Str__Url("https://openrouter.ai/api")       # OpenRouter api
URL__OPEN_ROUTER__API__V1_MODELS : Safe_Str__Url = URL__OPEN_ROUTER__API + "/v1/models"             # OpenRouter models


# OpenRouter-specific regex patterns for Safe_Str validation
# These patterns define what characters to REMOVE (anything not matching is replaced with _)

REGEX__OPEN_ROUTER__DESCRIPTION = r'[^a-zA-Z0-9_ ()\[\]\-+=:;,.?*/\\×\\\n`&"\'#’%<>“”~—‑\u202f‐→–{}\xa0$@|!]'
REGEX__OPEN_ROUTER__MODEL_ID    = r'[^a-zA-Z0-9/\-.:_]'             # Allows: alphanumeric, /, -, ., :, _
REGEX__OPEN_ROUTER__MODEL_NAME  = r'[^a-zA-Z0-9:\s.\-()+]🐬'        # Allows: alphanumeric, :, space, ., -, (, ) + 🐬
REGEX__OPEN_ROUTER__MODEL_SLUG  = r'[^a-zA-Z0-9/\-._]'              # Allows: alphanumeric, /, -, ., _
REGEX__OPEN_ROUTER__MODALITY    = r'[^a-zA-Z0-9+\->]'               # Allows: alphanumeric, +, -, >
REGEX__OPEN_ROUTER__TOKENIZER   = r'[^a-zA-Z0-9\-_\s]'              # Allows: alphanumeric, -, _, space
REGEX__OPEN_ROUTER__PARAMETER   = r'[^a-zA-Z0-9_]'                  # Allows: alphanumeric, _