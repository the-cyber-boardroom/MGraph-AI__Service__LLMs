import pytest
from unittest                                                                                        import TestCase
from osbot_utils.testing.__                                                                          import __
from osbot_utils.type_safe.Type_Safe                                                                 import Type_Safe
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects                                                                       import base_classes
from osbot_utils.utils.Env                                                                           import get_env
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Call              import Schema__LLM__Tool__Call
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Response          import Schema__LLM__Tool__Response
from mgraph_ai_service_llms.platforms.open_router.service.Service__LLM__Tools                        import Service__LLM__Tools
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                       import Service__Open_Router, ENV_NAME_OPEN_ROUTER__API_KEY
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Definition        import Schema__LLM__Tool__Definition
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Request           import Schema__LLM__Tool__Request
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers        import Schema__Open_Router__Providers
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Supported_Models import Schema__Open_Router__Supported_Models
from tests.unit.Service__Fast_API__Test_Objs import setup__service_fast_api_test_objs


class test_Service__LLM__Tools(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # Setup expensive resources once
        cls.local_objs = setup__service_fast_api_test_objs()
        cls.service = Service__LLM__Tools()

        # Create reusable test tool definition
        cls.echo_description  = "Message to echo"
        cls.echo_tool = Schema__LLM__Tool__Definition(
            name        = "echo_message"                                                          ,
            description = "Echo back a message"                                                   ,
            parameters  = { "type"       : "object"                                               ,
                            "properties" : { "message" : { "type"        : "string"               ,
                                                           "description" : cls.echo_description   }},
                            "required"   : ["message"]                                            }
        )

        cls.math_tool = Schema__LLM__Tool__Definition(
            name        = "calculate"                                                             ,
            description = "Perform basic math"                                                    ,
            parameters  = { "type"       : "object"                                                        ,
                           "properties" : { "operation" : { "type": "string", "enum": ["+", "-", "*", "/"] },
                                           "a"        : { "type": "number"                                 },
                                           "b"        : { "type": "number"                                 }},
                           "required"   : ["operation", "a", "b"]                                          }
        )

    def test__init__(self):                                                                         # Test service initialization
        with self.service as _:
            assert type(_)         is Service__LLM__Tools
            assert base_classes(_) == [Type_Safe, object]

            # Verify sub-service initialized
            assert type(_.open_router) is Service__Open_Router

            assert False # force unit test failure

    #@patch.object(Service__Open_Router, 'chat_completion')
    def test_execute_with_tool(self):                                                    # Test tool execution with mocked LLM
        # Create request
        user_prompt = "Echo hello!"
        request     = Schema__LLM__Tool__Request(user_prompt     = user_prompt                                               ,
                                                 tool_definition = self.echo_tool                                            ,
                                                 model           = Schema__Open_Router__Supported_Models.Open_AI__GPT_4o_Mini
                                                 )

        assert request.obj() == __(system_prompt   = None,
                                   model           = 'openai/gpt-4o-mini',
                                   provider        = None,
                                   temperature     = 0.0,
                                   max_tokens      = 5000,
                                   force_tool_use  = True,
                                   user_prompt     ='Echo hello!',
                                   tool_definition = __(name=       'echo_message',
                                                        description ='Echo back a message',
                                                        parameters  =__(type       = 'object',
                                                                        properties = __(message=__(type        = 'string',
                                                                                                   description = self.echo_description)),
                                                                        required=['message'])))
        # Execute
        with self.service.execute_with_tool(request) as response:
            assert type(response) is Schema__LLM__Tool__Response
            response.print()
            cache_id = response.cache_id
            pprint(cache_id)
            #cache_data = self.service(cache_id)
            return
            assert type(response) is Schema__LLM__Tool__Response
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0].name == "echo_message"
            assert response.tool_calls[0].arguments == {"message": "Hello"}
            assert response.tool_calls[0].id == "call_123"
            assert response.requires_action is True
            assert response.cache_id == "cache_abc"
            assert response.provider_used == "openai"

    #@patch.object(Service__Open_Router, 'chat_completion')
    def test_execute_with_text_response(self, mock_chat):                                           # Test when LLM returns text instead of tool call
        # Mock response with text content
        mock_chat.return_value = { "choices": [{ "message": { "content": "I would use the echo tool to respond" }}],
                                   "provider": "groq"                                                                     }

        request = Schema__LLM__Tool__Request(
            user_prompt     = "How would you echo hello?"                                         ,
            tool_definition = self.echo_tool                                                      ,
            force_tool_use  = False                                                               # Not forcing tool use
        )

        with self.service.execute_with_tool(request) as response:
            assert response.response_content == "I would use the echo tool to respond"
            assert len(response.tool_calls) == 0
            assert response.requires_action is False

    def test_convert_to_openrouter_tool(self):                                                      # Test tool definition conversion
        with self.service as _:
            openrouter_tool = _._convert_to_openrouter_tool(self.math_tool)

            assert openrouter_tool.type == "function"
            assert openrouter_tool.function.name == "calculate"
            assert openrouter_tool.function.description == "Perform basic math"
            assert openrouter_tool.function.parameters == self.math_tool.parameters

    def test_validate_tool_arguments_valid(self):                                                   # Test validation with valid arguments
        with self.service as _:
            tool_call = Schema__LLM__Tool__Call(name      = "calculate"                                                           ,
                                                arguments = {"operation": "+", "a": 42, "b": 17})

            result = _.validate_tool_arguments(tool_call, self.math_tool)

            assert result["valid"] is True
            assert result["errors"] == []
            assert result["data"] == {"operation": "+", "a": 42, "b": 17}

    def test_validate_tool_arguments_missing_required(self):                                        # Test validation with missing required field
        with self.service as _:
            tool_call = Schema__LLM__Tool__Call(
                name      = "calculate"                                                           ,
                arguments = {"operation": "+", "a": 42}                                           # Missing 'b'
            )

            result = _.validate_tool_arguments(tool_call, self.math_tool)

            assert result["valid"] is False
            assert "Missing required field: b" in result["errors"]

    def test_validate_tool_arguments_wrong_type(self):                                              # Test validation with wrong type
        with self.service as _:
            tool_call = Schema__LLM__Tool__Call(
                name      = "calculate"                                                           ,
                arguments = {"operation": "+", "a": "not_a_number", "b": 17}
            )

            result = _.validate_tool_arguments(tool_call, self.math_tool)

            assert result["valid"] is False
            assert "Field a should be number" in result["errors"]

    def test_validate_tool_arguments_invalid_enum(self):                                            # Test validation with invalid enum value
        with self.service as _:
            tool_call = Schema__LLM__Tool__Call(
                name      = "calculate"                                                           ,
                arguments = {"operation": "%", "a": 42, "b": 17}                                  # % not in enum
            )

            # Note: Basic validation doesn't check enum values currently
            # This is a known limitation that could be enhanced
            result = _.validate_tool_arguments(tool_call, self.math_tool)

            # Currently passes because we only check basic types
            assert result["valid"] is True                                                          # Would be False with enum validation

    #@patch.object(Service__Open_Router, 'chat_completion')
    def test_execute_with_provider_routing(self, mock_chat):                                        # Test provider routing
        mock_chat.return_value = { "choices": [{ "message": { "tool_calls": [] }}]                ,
                                   "provider": "groq"                                             }

        request = Schema__LLM__Tool__Request(
            user_prompt     = "Test"                                                              ,
            tool_definition = self.echo_tool                                                      ,
            provider        = Schema__Open_Router__Providers.GROQ
        )
        assert request.obj() == __()

    @pytest.mark.skipif(
        get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None,
        reason="Requires OPEN_ROUTER__API_KEY environment variable"
    )
    def test_execute_with_real_api(self):                                                           # Test with actual API call
        request = Schema__LLM__Tool__Request(
            user_prompt     = "Echo the message 'test'"                                           ,
            system_prompt   = "You are a helpful assistant. Use the echo_message tool."           ,
            tool_definition = self.echo_tool                                                      ,
            model           = Schema__Open_Router__Supported_Models.Open_AI__GPT_4o_Mini          ,
            temperature     = 0.1                                                                 ,
            force_tool_use  = True
        )

        with self.service.execute_with_tool(request) as response:
            # Should have made a tool call
            assert len(response.tool_calls) > 0
            assert response.tool_calls[0].name == "echo_message"
            assert "test" in str(response.tool_calls[0].arguments).lower()
            assert response.requires_action is True