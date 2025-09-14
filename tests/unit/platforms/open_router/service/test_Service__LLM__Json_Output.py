from unittest                                                                                            import TestCase
from osbot_utils.testing.__                                                                              import __, __SKIP__
from osbot_utils.utils.Objects                                                                           import base_classes
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.type_safe.primitives.domains.llm.safe_str.Safe_Str__LLM__Model_Id                       import Safe_Str__LLM__Model_Id
from osbot_fast_api.api.transformers.Type_Safe__To__Json                                                 import Type_Safe__To__Json
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Json_Extract__Request      import Schema__Json_Extract__Request
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Json_Extract__Response     import Schema__Json_Extract__Response
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Message_Content              import Safe_Str__Message_Content
from mgraph_ai_service_llms.platforms.open_router.service.Service__LLM__Json_Output                      import Service__LLM__Json_Output
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                           import Service__Open_Router
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers            import Schema__Open_Router__Providers
from mgraph_ai_service_llms.service.llms.prompts.schemas.Schema__Facts                                   import Schema__Facts
from tests.unit.Service__Fast_API__Test_Objs                                                             import setup__service_fast_api_test_objs


class test_Service__LLM__Json_Output(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_objs    = setup__service_fast_api_test_objs()
        cls.service      = Service__LLM__Json_Output()
        cls.test_text    = "In this test suite, there are 5 classes and 7 tests."
        transformer      = Type_Safe__To__Json()                                                             # Generate JSON schema from Type_Safe class
        cls.facts_schema = transformer.convert_class(Schema__Facts)

    def test__init__(self):                                                                                  # Test service initialization
        with Service__LLM__Json_Output() as _:
            assert type(_)                   is Service__LLM__Json_Output
            assert base_classes(_)           == [Type_Safe, object]
            assert type(_.open_router)       is Service__Open_Router
            assert type(_.default_model)     is Safe_Str__LLM__Model_Id
            assert _.default_model           == "openai/gpt-oss-20b"
            assert _.default_provider        == Schema__Open_Router__Providers.GROQ

    def test_extract__returns_response_schema(self):                                                         # Test that extract returns Schema__Json_Extract_Response
        with self.service as _:

            result = _.extract(text_content  = self.test_text                     ,
                               output_schema = self.facts_schema                  ,
                               model         = "openai/gpt-oss-20b"               ,
                               provider      = Schema__Open_Router__Providers.GROQ)

            assert type(result)           is Schema__Json_Extract__Response                                 # Result should be Schema__Json_Extract_Response
            assert type(result.json_data) is dict
            assert result.obj()           == __(cache_id  = __SKIP__            ,
                                                duration  = __SKIP__            ,
                                                model     = 'openai/gpt-oss-20b',
                                                provider  = 'groq'              ,
                                                json_data = __SKIP__            ,
                                                tokens    = __SKIP__            )
            assert result.duration > 0
            assert result.tokens   > 0
            assert 'facts'   in result.json_data                                                            # JSON data should match expected structure
            assert 'summary' in result.json_data
            assert len(result.json_data['facts']) > 0

    # todo: rewrite this without using mocks and monkey patch
    # def test_extract__handles_invalid_json(self):                                                            # Test handling of invalid JSON
    #     with self.service as _:
    #         # Mock with invalid JSON response
    #         _.open_router.chat_completion = lambda **kwargs: {
    #             "choices": [{
    #                 "message": {
    #                     "content": "This is not JSON at all"
    #                 }
    #             }],
    #         }
    #
    #         result = _.extract(text_content  = self.test_text   ,
    #                            output_schema = self.facts_schema)
    #
    #         # Should return response with empty dict
    #         assert type(result)           is Schema__Json_Extract__Response
    #         assert result.json_data       == {}

    def test_schema__json_extract_request(self):                                                             # Test request schema
        request = Schema__Json_Extract__Request(text_content  = Safe_Str__Message_Content("Extract data from this")    ,
                                                output_schema = self.facts_schema                           )
        assert type(request.text_content)  is Safe_Str__Message_Content
        assert type(request.output_schema) is dict
        assert request.model               is None
        assert request.provider            is None
        assert request.temperature         == 0.0
        assert request.max_tokens          == 5000

    #@pytest.mark.skip(reason="Requires OpenRouter API key")
    def test_extract__with_actual_api(self):                                                                 # Test with real API call
        with self.service as _:
            result = _.extract(text_content  = self.test_text                                  ,
                               output_schema = self.facts_schema                               ,
                               model         = Safe_Str__LLM__Model_Id('openai/gpt-oss-20b')   ,
                               provider      = Schema__Open_Router__Providers.GROQ             ,
                               temperature   = 0.0                                             )

            # Should return valid response
            assert type(result)        is Schema__Json_Extract__Response
            assert result.json_data    != {}

            # Client would convert back to Type_Safe
            facts = Schema__Facts.from_json(result.json_data)
            assert type(facts)         is Schema__Facts
            assert len(facts.facts)    > 0                                                                   # Should extract some facts
            assert facts.summary       != ''                                                                 # Should have a summary

    def test_client_side_conversion_flow(self):                                                              # Test the full client-side flow
        # Step 1: Client converts Type_Safe to JSON Schema
        transformer = Type_Safe__To__Json()
        schema      = transformer.convert_class(Schema__Facts)

        # Step 2: Client calls service with schema
        with self.service as _:
            result = _.extract(text_content  = "There are 5 test in this test class",
                               output_schema = schema     )

        # Step 3: Client converts JSON back to Type_Safe
        facts = Schema__Facts.from_json(result.json_data)

        # Verify full flow worked
        assert type(facts)         is Schema__Facts
        assert len(facts.facts)    > 0
