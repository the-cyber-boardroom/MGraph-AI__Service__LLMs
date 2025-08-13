import pytest
from unittest                                                                      import TestCase
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Objects                                                      import base_classes
from osbot_utils.utils.Env                                                          import set_env, get_env, load_dotenv
from mgraph_ai_service_llms.service.llms.providers.open_router.Provider__OpenRouter import Provider__OpenRouter, ENV_NAME_OPEN_ROUTER__API_KEY


class test_Provider__OpenRouter(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.provider = Provider__OpenRouter()
        load_dotenv()

    def test__init__(self):
        with self.provider as _:
            assert type(_)         == Provider__OpenRouter
            assert base_classes(_) == [Type_Safe, object]
            assert _.api_url       == "https://openrouter.ai/api/v1/chat/completions"
            assert _.api_key_name  == ENV_NAME_OPEN_ROUTER__API_KEY
            assert _.http_referer  == "https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs"

    def test_api_key(self):
        # Test with environment variable
        test_key = "test-key-12345"
        original_value = get_env(ENV_NAME_OPEN_ROUTER__API_KEY)

        try:
            set_env(ENV_NAME_OPEN_ROUTER__API_KEY, test_key)
            assert self.provider.api_key() == test_key

            # Test with no key
            set_env(ENV_NAME_OPEN_ROUTER__API_KEY, "")
            assert self.provider.api_key() == ""

        finally:
            if original_value:
                set_env(ENV_NAME_OPEN_ROUTER__API_KEY, original_value)
            else:
                set_env(ENV_NAME_OPEN_ROUTER__API_KEY, "")

    def test_execute__with_actual_api(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test payload with minimal response
        test_payload = {
            "model": "mistralai/mistral-small-3.2-24b-instruct:free",
            "messages": [
                {"role": "user", "content": "Say 'test' in one word"}
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }

        # Execute actual API call
        result = self.provider.execute(test_payload)

        # Verify response structure
        assert type(result) is dict
        assert 'id'      in result
        assert 'choices' in result
        assert 'usage'   in result

        # Check choices structure
        assert len(result['choices']) > 0
        first_choice = result['choices'][0]
        assert 'message' in first_choice
        assert 'role'    in first_choice['message']
        assert 'content' in first_choice['message']

        # Check usage structure
        usage = result['usage']
        assert 'prompt_tokens'     in usage
        assert 'completion_tokens' in usage
        assert 'total_tokens'      in usage

    def test_execute__with_invalid_api_key(self):
        # Save original key
        original_key = get_env(ENV_NAME_OPEN_ROUTER__API_KEY)

        try:
            # Set invalid key
            set_env(ENV_NAME_OPEN_ROUTER__API_KEY, "invalid-key-12345")

            test_payload = {
                "model": "mistralai/mistral-small-3.2-24b-instruct:free",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }

            # Should raise ValueError due to invalid API key
            with self.assertRaises(ValueError) as context:
                self.provider.execute(test_payload)

            # Error message should contain authentication related error
            error_str = str(context.exception)
            assert 'auth' in error_str.lower() or 'key' in error_str.lower() or 'unauthorized' in error_str.lower()

        finally:
            # Restore original key
            if original_key:
                set_env(ENV_NAME_OPEN_ROUTER__API_KEY, original_key)
            else:
                set_env(ENV_NAME_OPEN_ROUTER__API_KEY, "")

    def test_execute__with_invalid_model(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        test_payload = {
            "model": "invalid/model-that-does-not-exist",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        }

        # Should raise ValueError due to invalid model
        with self.assertRaises(ValueError) as context:
            self.provider.execute(test_payload)

        error_str = str(context.exception)
        assert 'model' in error_str.lower() or 'invalid' in error_str.lower()
