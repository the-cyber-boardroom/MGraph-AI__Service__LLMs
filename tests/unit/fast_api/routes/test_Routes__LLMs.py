import pytest
from unittest                                                                       import TestCase
from osbot_fast_api.api.routes.Fast_API__Routes                                     import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Env                                                          import load_dotenv, get_env
from osbot_utils.utils.Misc                                                         import list_set
from osbot_utils.utils.Objects                                                      import base_classes
from mgraph_ai_service_llms.fast_api.routes.Routes__LLMs                            import Routes__LLMs, TAG__ROUTES_LLMS
from mgraph_ai_service_llms.service.llms.LLM__Service                               import LLM__Service
from mgraph_ai_service_llms.service.llms.providers.open_router.Provider__OpenRouter import ENV_NAME_OPEN_ROUTER__API_KEY
from mgraph_ai_service_llms.service.schemas.Schema__LLM__Models                     import Schema__LLM__Models
from tests.unit.Service__Fast_API__Test_Objs                                        import setup__service_fast_api_test_objs


class test_Routes__LLMs(TestCase):

    @classmethod
    def setUpClass(cls):
        # if in_github_action():
        #     pytest.skip("Failed intermittently in GitHub")
        setup__service_fast_api_test_objs()
        cls.routes_llms = Routes__LLMs()

    def test_setUpClass(self):
        with self.routes_llms as _:
            assert type(_)         == Routes__LLMs
            assert base_classes(_) == [Fast_API__Routes, Type_Safe, object]
            assert _.tag           == 'llms'
            assert type(_.llm_service) == LLM__Service

    def test_constants(self):
        assert TAG__ROUTES_LLMS    == 'llms'

    def test_models(self):
        result = self.routes_llms.models()
        assert type(result) is dict
        assert 'models'     in result
        models = result['models']
        assert len(models) == 9

        # Check first model structure
        first_model = models[0]
        assert list_set(first_model)   == ['id', 'is_free', 'name', 'provider']
        assert first_model['name']     == 'MISTRAL_SMALL_FREE'
        assert first_model['id']       == 'mistralai/mistral-small-3.2-24b-instruct:free'
        assert first_model['is_free']  is True
        assert first_model['provider'] == 'mistralai'

        # Check a paid model
        gpt_model = next(m for m in models if m['name'] == 'GPT_4O_MINI')
        assert gpt_model['is_free' ]  is False
        assert gpt_model['provider'] == 'openai'

    @pytest.mark.skip("not using cache")
    def test_complete__with_actual_api_call(self):

        load_dotenv()
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Make actual API call with minimal tokens
        result = self.routes_llms.complete(
            prompt      = "Say 'hello' in one word",
            model       = Schema__LLM__Models.MISTRAL_SMALL_FREE,
            temperature = 0.1,
            max_tokens  = 10
        )

        assert type(result) is dict
        assert 'model'        in result
        assert 'prompt'       in result
        assert 'response'     in result
        assert 'usage'        in result
        assert 'raw_response' in result

        assert result['model']  == Schema__LLM__Models.MISTRAL_SMALL_FREE.value
        assert result['prompt'] == "Say 'hello' in one word"
        assert len(result['response']) > 0  # Should have some response
        assert type(result['usage']) is dict