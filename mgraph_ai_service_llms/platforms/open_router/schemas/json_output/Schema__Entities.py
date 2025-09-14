from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text         import Safe_Str__Text
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Entity import Schema__Entity

class Schema__Entities(Type_Safe):                                                                   # Collection of entities
    entities : list[Schema__Entity]
    summary  : Safe_Str__Text