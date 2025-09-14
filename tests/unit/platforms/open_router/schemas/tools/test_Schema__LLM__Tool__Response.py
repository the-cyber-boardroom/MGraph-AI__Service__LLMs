from unittest                                                                               import TestCase
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                       import Type_Safe__List
from osbot_utils.utils.Objects                                                              import base_classes
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Call     import Schema__LLM__Tool__Call
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Response import Schema__LLM__Tool__Response


class test_Schema__LLM__Tool__Response(TestCase):

    def test__init__(self):                                                                         # Test response initialization
        with Schema__LLM__Tool__Response() as _:
            assert type(_)         is Schema__LLM__Tool__Response
            assert base_classes(_) == [Type_Safe, object]

            # Collections should be Type_Safe variants
            assert type(_.tool_calls) is Type_Safe__List
            assert _.tool_calls       == []                                                         # Empty list
            assert _.response_content is None                                                       # Optional text
            assert _.requires_action  is False                                                      # Default false
            assert _.cache_id         is None                                                       # Optional
            assert _.model_used       == ''                                                         # Safe_Str empty
            assert _.provider_used    is None                                                       # Optional

    def test_with_tool_calls(self):                                                                 # Test response with multiple tool calls
        with Schema__LLM__Tool__Response() as _:
            # Create tool calls
            call1 = Schema__LLM__Tool__Call(name="get_weather", arguments={"location": "London"})
            call2 = Schema__LLM__Tool__Call(name="get_weather", arguments={"location": "Paris"})

            _.tool_calls = [call1, call2]
            _.requires_action = True
            _.model_used = "openai/gpt-4o-mini"
            _.provider_used = "openai"
            _.cache_id = "aabbccddee"

            assert len(_.tool_calls) == 2
            assert _.tool_calls[0].name == "get_weather"
            assert _.tool_calls[1].arguments["location"] == "Paris"
            assert _.requires_action is True

    def test_with_text_response(self):                                                              # Test response with text content
        with Schema__LLM__Tool__Response() as _:
            _.response_content = "I need to use the weather tool to answer your question"
            _.requires_action = False                                                               # No tools needed
            _.model_used = "openai/gpt-oss-20b"

            assert _.response_content == "I need to use the weather tool to answer your question"
            assert _.requires_action is False
            assert len(_.tool_calls) == 0                                                           # No tool calls

    def test_json_serialization_complex(self):                                                      # Test complex response serialization
        with Schema__LLM__Tool__Response() as original:
            # Add multiple tool calls
            original.tool_calls = [
                Schema__LLM__Tool__Call(name="func1", arguments={"x": 1}, id="id1"),
                Schema__LLM__Tool__Call(name="func2", arguments={"y": 2}, id="id2")
            ]
            original.response_content = "Processing..."
            original.requires_action  = True
            original.cache_id         = "aabbccddee"
            original.model_used       = "openai/gpt-4o-mini"
            original.provider_used    = "openai"

            # Serialize
            json_data = original.json()

            # Deserialize
            with Schema__LLM__Tool__Response.from_json(json_data) as restored:
                assert len(restored.tool_calls)              == 2
                assert restored.tool_calls[0].name           == "func1"
                assert restored.tool_calls[1].arguments["y"] == 2
                assert restored.response_content             == "Processing..."
                assert restored.requires_action              is True
                assert restored.cache_id                     == "aabbccddee"