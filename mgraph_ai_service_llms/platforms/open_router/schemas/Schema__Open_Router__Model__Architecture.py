from typing                                                                                 import List, Optional
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                     import Safe_Str
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Modality   import Safe_Str__Open_Router__Modality
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Tokenizer  import Safe_Str__Open_Router__Tokenizer

class Schema__Open_Router__Model__Architecture(Type_Safe):
    modality          : Safe_Str__Open_Router__Modality                         # e.g., "text+image->text"
    input_modalities  : List[Safe_Str]                                          # e.g., ["text", "image"]
    output_modalities : List[Safe_Str]                                          # e.g., ["text"]
    tokenizer         : Safe_Str__Open_Router__Tokenizer                        # e.g., "Mistral", "Other"
    instruct_type     : Optional[Safe_Str] = None                               # May be null







