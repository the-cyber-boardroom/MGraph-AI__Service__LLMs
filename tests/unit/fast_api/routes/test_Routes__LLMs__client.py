import pytest
from unittest                                                                       import TestCase
from osbot_utils.utils.Env                                                          import get_env
from mgraph_ai_service_llms.service.llms.providers.open_router.Provider__OpenRouter import ENV_NAME_OPEN_ROUTER__API_KEY
from mgraph_ai_service_llms.service.schemas.Schema__LLM__Models                     import Schema__LLM__Models
from tests.unit.Service__Fast_API__Test_Objs                                        import setup__service_fast_api_test_objs, TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__LLMs__client(TestCase):
    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

    def test__llms__models(self):
        response = self.client.get('/llms/models')
        assert response.status_code == 200

        result = response.json()
        assert 'models' in result
        models = result['models']

        # Verify we have all expected models
        assert len(models) == len(Schema__LLM__Models)
        assert len(models) == 9

        # Check structure of first model
        first_model = models[0]
        assert first_model['name']     == 'MISTRAL_SMALL_FREE'
        assert first_model['is_free']  == True
        assert first_model['provider'] == 'mistralai'

        # Verify all model names
        model_names = [m['name'] for m in models]
        expected_names = [model.name for model in Schema__LLM__Models]
        assert model_names == expected_names

    def test__llms__complete__missing_prompt(self):
        response = self.client.post('/llms/complete', json={})
        assert response.status_code == 400  # Unprocessable Entity - missing required field

        # Check error details
        error_detail = response.json()
        assert 'detail' in error_detail
        assert any('prompt' in str(err).lower() for err in error_detail['detail'])

    #@pytest.mark.skip("client.post needs fixing")
    def test__bug__llms__complete__with_prompt(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        request_data = {  "prompt"     : "Reply with just 'OK'",
                          "model"      : "mistralai/mistral-small-3.2-24b-instruct:free",
                          "temperature": 0.1,
                          "max_tokens" : 5 }

        response = self.client.post('/llms/complete', json=request_data)
        assert response.status_code == 400
        assert response.json() == {'detail': [{ 'input': None               ,
                                                'loc' : ['query', 'prompt'] ,
                                                'msg' : 'Field required'    ,
                                                'type': 'missing'           }]}

        # assert response.status_code == 200      # BUG:
        #
        # result = response.json()
        # assert 'model'    in result
        # assert 'prompt'   in result
        # assert 'response' in result
        # assert 'usage'    in result
        #
        # assert result['prompt'] == "Reply with just 'OK'"
        # assert len(result['response']) > 0

    def test__regression__llms__request_hash_is_always_different(self):
        response = self.client.post('/llms/extract-facts-request-hash', json={})
        assert response.json() == { 'model'       : 'openai/gpt-5-nano'                 ,
                                    'result'      : '55cda1aba2'                        ,
                                    'text_content': 'This is a text about GenAI and MCP'}        # these should always be the same (given the same input)


