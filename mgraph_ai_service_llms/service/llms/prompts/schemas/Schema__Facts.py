from typing                                                           import List
from osbot_utils.type_safe.Type_Safe                                  import Type_Safe
from mgraph_ai_service_llms.service.llms.prompts.schemas.Schema__Fact import Schema__Fact


class Schema__Facts(Type_Safe):                     # Collection of extracted facts.
    facts  : List[Schema__Fact]
    summary: str                                    # Brief summary of the main points
