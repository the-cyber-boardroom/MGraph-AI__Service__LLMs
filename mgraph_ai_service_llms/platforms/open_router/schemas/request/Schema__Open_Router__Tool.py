from typing                                                                                           import Literal
from osbot_utils.type_safe.Type_Safe                                                                  import Type_Safe
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Tool__Function import Schema__Open_Router__Tool__Function


class Schema__Open_Router__Tool(Type_Safe):                 # OpenRouter tool/function definition
    type     : Literal["function"] = "function"
    function : Schema__Open_Router__Tool__Function
