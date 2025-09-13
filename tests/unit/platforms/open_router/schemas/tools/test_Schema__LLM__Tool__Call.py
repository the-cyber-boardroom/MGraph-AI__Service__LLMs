from unittest                                                                           import TestCase
from osbot_utils.testing.__                                                             import __
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.utils.Objects                                                          import base_classes
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Call import Schema__LLM__Tool__Call


class test_Schema__LLM__Tool__Call(TestCase):

    def test__init__(self):                                                                         # Test tool call initialization
        with Schema__LLM__Tool__Call() as _:
            assert type(_)         is Schema__LLM__Tool__Call
            assert base_classes(_) == [Type_Safe, object]

            assert _.name      == ''                                                                # Safe_Str empty
            assert _.arguments == {}                                                                # Empty dict
            assert _.id        is None                                                              # Optional ID

            assert _.obj() == __(name      = ''    ,
                                 arguments = __()  ,
                                 id        = None  )

    def test_with_arguments(self):                                                                  # Test tool call with arguments
        with Schema__LLM__Tool__Call() as _:
            _.name = "get_weather"
            _.arguments = { "location": "London", "unit": "celsius" }
            _.id = "call_123abc"

            assert _.arguments["location"] == "London"
            assert _.arguments["unit"]     == "celsius"
            assert _.id                    == "call_123abc"

    def test_json_serialization(self):                                                              # Test JSON round-trip for tool call
        with Schema__LLM__Tool__Call() as original:
            original.name = "calculate"
            original.arguments = {"operation": "+", "a": 42, "b": 17}
            original.id = "call_xyz789"

            json_data = original.json()

            with Schema__LLM__Tool__Call.from_json(json_data) as restored:
                assert restored.obj() == original.obj()
                assert restored.arguments["a"] == 42                                               # Numbers preserved
