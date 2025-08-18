from osbot_utils.type_safe.Type_Safe                                                                 import Type_Safe
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model__Pricing__Float import Schema__Open_Router__Model__Pricing__Float


# note some models don't have input_cache_read or input_cache_write
#      the "openrouter/auto" model is a different one, where its pricing value is set to
#           {   "prompt"    : "-1",
#               "completion": "-1"},

class Schema__Open_Router__Model__Pricing(Type_Safe):
    prompt             : Schema__Open_Router__Model__Pricing__Float = None      # Cost per token for prompts
    completion         : Schema__Open_Router__Model__Pricing__Float = None      # Cost per token for completions
    request            : Schema__Open_Router__Model__Pricing__Float = None      # Cost per request
    image              : Schema__Open_Router__Model__Pricing__Float = None      # Cost for image processing
    audio              : Schema__Open_Router__Model__Pricing__Float = None      # Cost for audio processing
    web_search         : Schema__Open_Router__Model__Pricing__Float = None      # Cost for web search
    internal_reasoning : Schema__Open_Router__Model__Pricing__Float = None      # Cost for internal reasoning
    input_cache_read   : Schema__Open_Router__Model__Pricing__Float = None
    input_cache_write  : Schema__Open_Router__Model__Pricing__Float = None

    def json(self):
        json_data = {}
        for field_name in self.__attr_names__():
            value = getattr(self, field_name, None)
            if value is not None:
                json_data[field_name] = value.to_original_string()
        return json_data