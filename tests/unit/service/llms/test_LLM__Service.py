import pytest
from unittest                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.utils.Objects                                          import base_classes
from osbot_utils.utils.Env                                              import get_env, load_dotenv
from mgraph_ai_service_llms.service.llms.LLM__Service                   import LLM__Service
from mgraph_ai_service_llms.service.llms.providers.Provider__OpenRouter import Provider__OpenRouter, ENV_NAME_OPEN_ROUTER__API_KEY


class test_LLM__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.llm_service = LLM__Service()
        load_dotenv()

    def test__init__(self):
        with self.llm_service as _:
            assert type(_)         == LLM__Service
            assert base_classes(_) == [Type_Safe, object]

    def test_provider(self):
        provider = self.llm_service.provider()
        assert type(provider) == Provider__OpenRouter

        # Test caching works - should return same instance
        provider2 = self.llm_service.provider()
        assert provider is provider2

    def test_execute_request__with_actual_api(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Execute actual request
        result = self.llm_service.execute_request(
            prompt      = "Reply with the word 'success' only",
            model       = "mistralai/mistral-small-3.2-24b-instruct:free",
            temperature = 0.1,
            max_tokens  = 10
        )

        # Verify result structure
        assert type(result) is dict
        assert 'model'        in result
        assert 'prompt'       in result
        assert 'response'     in result
        assert 'usage'        in result
        assert 'raw_response' in result

        # Verify values
        assert result['model']  == "mistralai/mistral-small-3.2-24b-instruct:free"
        assert result['prompt'] == "Reply with the word 'success' only"
        assert len(result['response']) > 0

        # Check response content makes sense
        response_lower = result['response'].lower()
        assert 'success' in response_lower or len(response_lower) > 0

        # Verify usage stats
        usage = result['usage']
        assert type(usage) is dict
        assert 'prompt_tokens'     in usage
        assert 'completion_tokens' in usage
        assert 'total_tokens'      in usage
        assert usage['total_tokens'] > 0

    def test_execute_request__with_defaults(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Execute with minimal params (using defaults)
        result = self.llm_service.execute_request(
            prompt = "Say 'hi'",
            model  = "mistralai/mistral-small-3.2-24b-instruct:free"
        )

        # Should work with default temperature (0.7) and max_tokens (1000)
        assert 'response' in result
        assert len(result['response']) > 0

    def test_execute_request__empty_response_handling(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        expected_error = "{'error': {'message': 'Input must have at least 1 token.', 'code': 400, 'metadata': {'provider_name': None}}}"
        with pytest.raises(ValueError, match=expected_error):
            self.llm_service.execute_request(prompt      = "" ,   # Empty prompt
                                             model       = "mistralai/mistral-small-3.2-24b-instruct:free",
                                             temperature = 0.1 ,
                                             max_tokens  = 1   )


    def test_execute_request__different_models(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test with different free models
        models_to_test = [
            "mistralai/mistral-small-3.2-24b-instruct:free",
            # Add more if needed, but be mindful of rate limits
        ]

        for model in models_to_test:
            result = self.llm_service.execute_request(
                prompt      = "Say 'test'",
                model       = model,
                temperature = 0.1,
                max_tokens  = 5
            )

            assert result['model'] == model
            assert len(result['response']) > 0
