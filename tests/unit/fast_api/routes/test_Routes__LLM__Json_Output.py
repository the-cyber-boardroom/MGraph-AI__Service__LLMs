from unittest                                                                                            import TestCase
from osbot_utils.utils.Objects                                                                           import base_classes
from osbot_fast_api.api.routes.Fast_API__Routes                                                          import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_fast_api.api.transformers.Type_Safe__To__Json                                                 import Type_Safe__To__Json
from mgraph_ai_service_llms.platforms.open_router.fast_api.routes.Routes__LLM__Json_Output               import Routes__LLM__Json_Output, TAG__ROUTES_LLM_JSON
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Json_Extract__Request      import Schema__Json_Extract__Request
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Json_Extract__Response     import Schema__Json_Extract__Response
from mgraph_ai_service_llms.platforms.open_router.service.Service__LLM__Json_Output                      import Service__LLM__Json_Output
from mgraph_ai_service_llms.service.llms.prompts.schemas.Schema__Facts                                   import Schema__Facts
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers            import Schema__Open_Router__Providers
from tests.unit.Service__Fast_API__Test_Objs                                                             import setup__service_fast_api_test_objs


class test_Routes__LLM__Json_Output(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_objs    = setup__service_fast_api_test_objs()
        cls.routes       = Routes__LLM__Json_Output()
        cls.test_text    = "There are 5 classes in this test suite and 7 tests methods."
        transformer      = Type_Safe__To__Json()                                                             # Generate test schema
        cls.facts_schema = transformer.convert_class(Schema__Facts)

    def test__init__(self):                                                                                  # Test route initialization
        with Routes__LLM__Json_Output() as _:
            assert type(_)                    is Routes__LLM__Json_Output
            assert base_classes(_)            == [Fast_API__Routes, Type_Safe, object]
            assert _.tag                      == TAG__ROUTES_LLM_JSON
            assert type(_.service_json)       is Service__LLM__Json_Output

    def test_extract(self):                                                                                  # Test main extraction endpoint
        with self.routes as _:

            request = Schema__Json_Extract__Request(text_content  = self.test_text   ,
                                                    output_schema = self.facts_schema)

            result = _.extract(request)

            assert type(result)           is Schema__Json_Extract__Response
            #assert result.cache_id        == "36bb54a47f"
            assert type(result.json_data) is dict
            assert result.duration        > 0
            assert result.tokens          > 0
            assert result.model           == 'openai/gpt-oss-20b'
            assert result.provider        == Schema__Open_Router__Providers.GROQ

            from osbot_utils.utils.Dev import pprint

    def test_setup_routes(self):                                                                             # Test route registration
        with self.routes as _:
            result = _.setup_routes()
            assert result is _                                                                               # Should return self for chaining






