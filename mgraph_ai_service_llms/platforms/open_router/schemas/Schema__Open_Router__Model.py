from typing                                                                                              import List, Optional
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Safe_Int                                                  import Safe_Int
from osbot_utils.type_safe.primitives.safe_str.text.Safe_Str__Text                                       import Safe_Str__Text
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_ID                import Safe_Str__Open_Router__Model_ID
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_Name              import Safe_Str__Open_Router__Model_Name
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_Slug              import Safe_Str__Open_Router__Model_Slug
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Parameter               import Safe_Str__Open_Router__Parameter
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model__Architecture       import Schema__Open_Router__Model__Architecture
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model__Pricing            import Schema__Open_Router__Model__Pricing
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model__Top_Provider       import Schema__Open_Router__Model__Top_Provider
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model__Per_Request_Limits import Schema__Open_Router__Model__Per_Request_Limits


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
