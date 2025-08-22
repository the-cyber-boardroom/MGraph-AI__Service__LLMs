import requests
from unittest                                           import TestCase
from urllib.parse                                       import urljoin
from fastapi                                            import FastAPI
from osbot_fast_api.api.Fast_API                        import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_fast_api.utils.Fast_API_Server               import Fast_API_Server
from osbot_utils.utils.Env                              import load_dotenv, get_env
from mgraph_ai_service_llms.fast_api.Service__Fast_API  import Service__Fast_API
from tests.unit.Service__Fast_API__Test_Objs            import setup__service_fast_api_test_objs


class test_Routes__LLMs__http(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.service__fast_api = setup__service_fast_api_test_objs().fast_api
        cls.service__app      = cls.service__fast_api.app()
        cls.fast_api_server   = Fast_API_Server(app=cls.service__app)
        cls.auth_headers      = {get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME): get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE)}
        cls.fast_api_server.start()


    @classmethod
    def tearDownClass(cls):
        cls.fast_api_server.stop()

    def test_setUpClass(self):
        with self.service__fast_api as _:
            assert type(_      ) is Service__Fast_API
            assert type(_.app()) is FastAPI

    def test__info__health(self):
        response = self.fast_api_server.requests_get('/info/health', headers=self.auth_headers)
        assert response.json() == {'status': 'ok'}

    def test__llms__extract_facts_request_hash(self):
        path     = 'llms/extract-facts-request-hash?'
        url      = urljoin(self.fast_api_server.url(), path)
        json_data = {}                  # note: add ability to pass multiple json payloads like {'text_content' : 'abc'} , which is not working
        response = requests.post(url, headers=self.auth_headers, json=json_data)
        assert response.json() == { 'model'       : 'openai/gpt-5-nano'                 ,
                                    'result'      : '67cbd5df21'                        ,   # hash should always be same (for the same input)
                                    'text_content': 'This is a text about GenAI and MCP' }



