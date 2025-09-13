from typing                                                                  import Dict, Any, Optional
from osbot_utils.type_safe.Type_Safe                                         import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                          import Safe_Str
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text import Safe_Str__Text

# todo: review the use of Any in the class type below

class Schema__LLM__Tool__Definition(Type_Safe):                                                       # Complete tool definition for LLM function calling
    name        : Safe_Str                                                                            # Tool/function name
    description : Safe_Str__Text                                                                            # Tool description
    parameters  : Dict[str, Any]                                                                      # JSON Schema format parameters

    # todo: remove these methods from this class
    def to_openai_format(self) -> Dict[str, Any]:                                                    # Convert to OpenAI function format
        return { "name"        : str(self.name)                                ,
                 "description" : str(self.description)                         ,
                 "parameters"  : self.parameters                               }

    def to_anthropic_format(self) -> Dict[str, Any]:                                                 # Convert to Anthropic tool format
        return { "name"         : str(self.name)                               ,
                 "description"  : str(self.description)                        ,
                 "input_schema" : self.parameters                              }