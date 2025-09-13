from unittest                                                                                        import TestCase
from osbot_utils.testing.__                                                                          import __
from osbot_utils.type_safe.Type_Safe                                                                 import Type_Safe
from osbot_utils.utils.Objects                                                                       import base_classes
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Request           import Schema__LLM__Tool__Request
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Definition        import Schema__LLM__Tool__Definition
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers        import Schema__Open_Router__Providers
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Supported_Models import Schema__Open_Router__Supported_Models

class test_Schema__LLM__Tool__Request(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # Setup test tool definition once
        cls.test_tool = Schema__LLM__Tool__Definition(
            name        = "calculate"                                                             ,
            description = "Perform basic math operations"                                         ,
            parameters  = { "type"       : "object"                                                        ,
                           "properties" : { "operation" : { "type": "string", "enum": ["+", "-", "*", "/"] },
                                           "a"        : { "type": "number"                                 },
                                           "b"        : { "type": "number"                                 }},
                           "required"   : ["operation", "a", "b"]                                          }
        )

    def test__init__(self):                                                                         # Test auto-initialization of request schema
        with Schema__LLM__Tool__Request() as _:
            assert type(_)         is Schema__LLM__Tool__Request
            assert base_classes(_) == [Type_Safe, object]

            # Test field initialization and defaults
            assert _.user_prompt     == ''                                                           # Safe_Str__Text empty
            assert _.system_prompt   is None                                                         # Optional field
            assert type(_.tool_definition) is Schema__LLM__Tool__Definition                          # Auto-initialized
            assert _.model           == Schema__Open_Router__Supported_Models.Open_AI__GPT_OSS_120b  # Explicit default
            assert _.provider        is None                                                         # Optional provider
            assert _.temperature     == 0.0                                                          # Lower temp for tools
            assert _.max_tokens      == 5000                                                         # Enough for tool calls
            assert _.force_tool_use  is True                                                         # Default to force

    def test__init__with_values(self):                                                               # Test with explicit values
        with Schema__LLM__Tool__Request() as _:
            _.user_prompt     = "Calculate 40 + 2"
            _.system_prompt   = "You are a math assistant"
            _.tool_definition = self.test_tool
            _.model           = Schema__Open_Router__Supported_Models.Open_AI__GPT_OSS_120b
            _.provider        = Schema__Open_Router__Providers.GROQ
            _.temperature     = 0.1
            _.max_tokens      = 500
            _.force_tool_use  = False

            assert _.obj().contains(__(user_prompt    = "Calculate 40 + 2"                        ,
                                       system_prompt  = "You are a math assistant"                ,
                                       temperature    = 0.1                                       ,
                                       max_tokens     = 500                                       ,
                                       force_tool_use = False                                     ))

            # Verify enums
            assert _.model    == Schema__Open_Router__Supported_Models.Open_AI__GPT_OSS_120b
            assert _.provider == Schema__Open_Router__Providers.GROQ


    def test_json_serialization(self):                                                              # Test JSON round-trip with full request
        with Schema__LLM__Tool__Request() as original:
            original.user_prompt     = "What's the weather in London?"
            original.system_prompt   = "Use the weather tool"
            original.tool_definition = self.test_tool
            original.model           = Schema__Open_Router__Supported_Models.Mistral_AI__Mistral_Small__Free
            original.provider        = Schema__Open_Router__Providers.CEREBRAS

            # Serialize to JSON
            json_data = original.json()
            with Schema__LLM__Tool__Request.from_json(json_data) as restored:
                assert restored.json() == original.json()
                assert restored.obj () == original.obj ()
                # Check critical fields match
                assert restored.user_prompt          == original.user_prompt
                assert restored.system_prompt        == original.system_prompt
                assert restored.tool_definition.name == original.tool_definition.name

                # Enums should be preserved
                assert restored.model   == original.model
                assert restored.provider == original.provider




