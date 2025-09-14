from unittest                                                                                            import TestCase
from osbot_fast_api.api.transformers.Type_Safe__To__Json                                                 import Type_Safe__To__Json
from osbot_utils.testing.__ import __, __SKIP__
from osbot_utils.utils.Dev import pprint

from mgraph_ai_service_llms.platforms.open_router.fast_api.Open_Router__Fast_API import FAST_API__BASE_PATH__OPEN_ROUTER
from mgraph_ai_service_llms.platforms.open_router.fast_api.routes.Routes__LLM__Json_Output               import Routes__LLM__Json_Output
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Json_Extract__Response import Schema__Json_Extract__Response
from mgraph_ai_service_llms.service.llms.prompts.schemas.Schema__Facts                                   import Schema__Facts
from tests.unit.Service__Fast_API__Test_Objs                                                             import setup__service_fast_api_test_objs, TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__LLM__Json_Output__client(TestCase):

    @classmethod
    def setUpClass(cls):                                                                                     # Setup test client
        with setup__service_fast_api_test_objs() as _:
            cls.fast_api                           = _.fast_api
            cls.client                             = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

        # Generate test schema
        transformer       = Type_Safe__To__Json()
        cls.facts_schema  = transformer.convert_class(Schema__Facts)
        cls.test_text     = "There are 5 classes in this test suite and 7 tests methods."
        cls.path__extract = f'/{FAST_API__BASE_PATH__OPEN_ROUTER}/llm-json/extract'

    def test__llm_json__extract(self):                                                                       # Test extraction endpoint via client
        request_data = { "text_content"  : self.test_text      ,
                         "output_schema" : self.facts_schema   ,
                         "model"         : 'openai/gpt-oss-20b',
                         "provider"      : "groq"              ,
                         "temperature"   : 0.0                 ,
                         "max_tokens"    : 5000                }

        response              = self.client.post(self.path__extract, json=request_data)
        json_extract_response = Schema__Json_Extract__Response.from_json(response.json())

        assert response.status_code == 200
        with json_extract_response as _:
            assert _.obj() == __(cache_id   = __SKIP__            ,
                                 duration   = __SKIP__            ,
                                 json_data  = __SKIP__            ,
                                 model      = 'openai/gpt-oss-20b',
                                 provider   = 'groq'              ,
                                 tokens     = __SKIP__            )
            assert _.duration > 0
            assert _.tokens   > 0



    def test__llm_json__extract__missing_fields(self):                                                       # Test validation with missing required fields
        request_data = { # Missing text_content and output_schema
                         "model": "openai/gpt-4o-mini"            }

        response = self.client.post(self.path__extract, json=request_data)

        assert response.status_code == 400                                                                  # Unprocessable Entity
        error = response.json()
        assert error == {'detail': [{ 'input': {'model': 'openai/gpt-4o-mini' },
                                      'loc'  : ['body', 'provider'            ],
                                      'msg'  : 'Field required'                ,
                                      'type' : 'missing'                       }]}

    def test__llm_json__extract__invalid_schema(self):                                                       # Test with invalid schema format
        request_data = { "text_content"  : self.test_text       ,
                         "output_schema" : "not a dict"         ,  # Should be dict
                         "model"         : "openai/gpt-4o-mini" ,
                         "provider"      : 'groq'               }

        response = self.client.post(self.path__extract, json=request_data)

        assert response.status_code == 400          # Type validation will fail
        assert response.json()     == {'detail': [{ 'input': 'not a dict',
                                                    'loc'  : ['body', 'output_schema'],
                                                    'msg'  : 'Input should be a valid dictionary',
                                                    'type' : 'dict_type'}]}
