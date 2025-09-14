from unittest                                                                                            import TestCase
from osbot_utils.utils.Objects                                                                           import base_classes
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Json_Extract__Response     import Schema__Json_Extract__Response

class test_Schema__Json_Extract_Response(TestCase):                                                          # Test response schema

    def test__init__(self):                                                                                  # Test response initialization
        with Schema__Json_Extract__Response() as _:
            assert type(_)         is Schema__Json_Extract__Response
            assert base_classes(_) == [Type_Safe, object]
            assert _.json_data     is None                                                                  # Auto-initialized
            assert _.cache_id      is None
            assert _.model         is None
            assert _.provider      is None

    def test_with_values(self):                                                                              # Test with actual values
        response = Schema__Json_Extract__Response(
            json_data = {"test": "data"}  ,
            cache_id  = "abc1234567"          ,
            model     = "openai/gpt-4o"   ,
            provider  = "openai"          ,
        )

        assert response.json_data == {"test": "data"}
        assert response.cache_id  == "abc1234567"