from typing                                                                                 import List, Optional
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                     import Safe_Str
from osbot_utils.type_safe.primitives.safe_str.text.Safe_Str__Text                          import Safe_Str__Text
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Modality   import Safe_Str__Open_Router__Modality
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Tokenizer  import Safe_Str__Open_Router__Tokenizer


class Schema__Open_Router__Model__Architecture(Type_Safe):
    modality          : Safe_Str__Open_Router__Modality                         # e.g., "text+image->text"
    input_modalities  : List[Safe_Str]                                          # e.g., ["text", "image"]
    output_modalities : List[Safe_Str]                                          # e.g., ["text"]
    tokenizer         : Safe_Str__Open_Router__Tokenizer                        # e.g., "Mistral", "Other"
    instruct_type     : Optional[Safe_Str] = None                               # May be null


# mgraph_ai_service_llms/platforms/open_router/schemas/Schema__Open_Router__Model__Pricing.py

from osbot_utils.type_safe.Type_Safe       import Type_Safe
from osbot_utils.type_safe.primitives.safe_float.Safe_Float import Safe_Float


class Schema__Open_Router__Model__Pricing(Type_Safe):
    prompt             : Safe_Float                                             # Cost per token for prompts
    completion         : Safe_Float                                             # Cost per token for completions
    request            : Safe_Float                                             # Cost per request
    image              : Safe_Float                                             # Cost for image processing
    audio              : Safe_Float                                             # Cost for audio processing
    web_search         : Safe_Float                                             # Cost for web search
    internal_reasoning : Safe_Float                                             # Cost for internal reasoning


# mgraph_ai_service_llms/platforms/open_router/schemas/Schema__Open_Router__Model__Top_Provider.py

from typing                                import Optional
from osbot_utils.type_safe.Type_Safe       import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Safe_Int import Safe_Int


class Schema__Open_Router__Model__Top_Provider(Type_Safe):
    context_length         : Safe_Int                                           # Maximum context length
    max_completion_tokens  : Optional[Safe_Int] = None                          # Maximum completion tokens
    is_moderated           : bool                                               # Whether the model is moderated


# mgraph_ai_service_llms/platforms/open_router/schemas/Schema__Open_Router__Model__Per_Request_Limits.py

from typing                                import Optional
from osbot_utils.type_safe.Type_Safe       import Type_Safe
from osbot_utils.helpers.safe_int.Safe_Int import Safe_Int


class Schema__Open_Router__Model__Per_Request_Limits(Type_Safe):
    prompt_tokens     : Optional[Safe_Int] = None                               # Max prompt tokens per request
    completion_tokens : Optional[Safe_Int] = None                               # Max completion tokens per request


# mgraph_ai_service_llms/platforms/open_router/schemas/Schema__Open_Router__Model.py

from typing                                                                                                    import List, Optional
from osbot_utils.type_safe.Type_Safe                                                                           import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Safe_Int                                                                     import Safe_Int
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_ID                      import Safe_Str__Open_Router__Model_ID
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_Name                    import Safe_Str__Open_Router__Model_Name
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_Slug                    import Safe_Str__Open_Router__Model_Slug
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Parameter                     import Safe_Str__Open_Router__Parameter
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model__Architecture             import Schema__Open_Router__Model__Architecture
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model__Pricing                  import Schema__Open_Router__Model__Pricing
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model__Top_Provider             import Schema__Open_Router__Model__Top_Provider
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model__Per_Request_Limits       import Schema__Open_Router__Model__Per_Request_Limits


class Schema__Open_Router__Model(Type_Safe):
    id                   : Safe_Str__Open_Router__Model_ID                      # Model ID e.g., "mistralai/mistral-medium-3.1"
    canonical_slug       : Safe_Str__Open_Router__Model_Slug                    # Canonical slug for the model
    hugging_face_id      : Safe_Str__Open_Router__Model_ID                      # Hugging Face model ID (may be empty)
    name                 : Safe_Str__Open_Router__Model_Name                    # Human-readable model name
    created              : Safe_Int                                             # Unix timestamp of creation
    description          : Safe_Str__Text                                       # Detailed model description
    context_length       : Safe_Int                                             # Maximum context length
    architecture         : Schema__Open_Router__Model__Architecture             # Architecture details
    pricing              : Schema__Open_Router__Model__Pricing                  # Pricing information
    top_provider         : Schema__Open_Router__Model__Top_Provider             # Top provider details
    per_request_limits   : Optional[Schema__Open_Router__Model__Per_Request_Limits] = None  # Per-request limits
    supported_parameters : List[Safe_Str__Open_Router__Parameter]               # List of supported parameters


# mgraph_ai_service_llms/platforms/open_router/schemas/Schema__Open_Router__Models__Response.py

from typing                                                                       import List
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model import Schema__Open_Router__Model


class Schema__Open_Router__Models__Response(Type_Safe):
    data : List[Schema__Open_Router__Model]                                     # List of available models