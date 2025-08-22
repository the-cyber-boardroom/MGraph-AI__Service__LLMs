import pytest
from unittest                                                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.utils.Objects                                                                          import base_classes
from osbot_utils.utils.Env                                                                              import get_env, load_dotenv
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                          import Service__Open_Router, ENV_NAME_OPEN_ROUTER__API_KEY
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router__Models                  import Service__Open_Router__Models
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router__Cost                    import Service__Open_Router__Cost
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Request_Headers  import Schema__Open_Router__Request_Headers
from tests.unit.Service__Fast_API__Test_Objs                                                            import setup__service_fast_api_test_objs


class test_Service__Open_Router(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        setup__service_fast_api_test_objs()
        cls.service = Service__Open_Router()
        if not get_env(ENV_NAME_OPEN_ROUTER__API_KEY):
            pytest.skip(f"skipping test because OpenRouter API key not found in environment variable: {ENV_NAME_OPEN_ROUTER__API_KEY}")

    def test__init__(self):
        with self.service as _:
            assert type(_)                 is Service__Open_Router
            assert base_classes(_)         == [Type_Safe, object]
            assert _.api_base_url          == "https://openrouter.ai/api"
            assert type(_.models_service) is Service__Open_Router__Models
            assert type(_.cost_service)   is Service__Open_Router__Cost

    def test_api_key(self):
        api_key = self.service.api_key()
        assert type(api_key) is str
        assert len(api_key)  > 0

    def test_chat_completion_url(self):
        url = self.service.chat_completion_url()
        assert url == "https://openrouter.ai/api/v1/chat/completions"

    def test_create_headers(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test basic headers
        headers = self.service.create_headers()
        assert type(headers)           is Schema__Open_Router__Request_Headers
        assert headers.x_include_provider is True

        # Test with max_cost
        headers = self.service.create_headers(max_cost = 0.01)
        assert headers.x_max_cost == 0.01

        # Test with provider
        headers = self.service.create_headers(provider = "openai")
        assert str(headers.x_provider) == "openai"

        # Test with include_provider = False
        headers = self.service.create_headers(include_provider = False)
        assert headers.x_include_provider is False

    def test_chat_completion__with_actual_api(self):

        # Test basic chat completion
        response = self.service.chat_completion(
            prompt      = "Reply with 'test' only",
            model       = "mistralai/mistral-small-3.2-24b-instruct:free",
            temperature = 0.1,
            max_tokens  = 10
        )

        # Verify response structure
        assert type(response) is dict
        assert 'id'      in response
        assert 'choices' in response
        assert 'usage'   in response

        # Check choices
        assert len(response['choices']) > 0
        choice = response['choices'][0]
        assert 'message' in choice
        assert 'content' in choice['message']
        assert len(choice['message']['content']) > 0

        # Check usage
        usage = response['usage']
        assert 'prompt_tokens'     in usage
        assert 'completion_tokens' in usage
        assert 'total_tokens'      in usage

        # Check cost breakdown if present
        if 'cost_breakdown' in response:
            cost = response['cost_breakdown']
            assert 'total_cost'   in cost
            assert 'model'        in cost

    def test_chat_completion__with_system_prompt(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        response = self.service.chat_completion(
            prompt        = "What is your role?",
            model         = "mistralai/mistral-small-3.2-24b-instruct:free",
            system_prompt = "You are a helpful assistant that always starts responses with 'SYSTEM:'",
            temperature   = 0.1,
            max_tokens    = 20
        )

        assert 'choices' in response
        content = response['choices'][0]['message']['content']
        # System prompt should influence the response
        assert len(content) > 0

    @pytest.mark.skip(reason="needs cache support")
    def test_chat_completion_stream__with_actual_api(self):

        # Collect streamed chunks
        chunks = []
        for chunk in self.service.chat_completion_stream(
            prompt      = "Count from 1 to 3",
            model       = "mistralai/mistral-small-3.2-24b-instruct:free",
            temperature = 0.1,
            max_tokens  = 20
        ):
            chunks.append(chunk)

        # Verify we got chunks
        assert len(chunks) > 0

        # First chunk should have the standard structure
        first_chunk = chunks[0]
        assert type(first_chunk) is dict
        assert 'id'      in first_chunk
        assert 'choices' in first_chunk

        # Collect all content
        full_content = ""
        for chunk in chunks:
            if 'choices' in chunk and len(chunk['choices']) > 0:
                delta = chunk['choices'][0].get('delta', {})
                if 'content' in delta:
                    full_content += delta['content']

        # Should have received some content
        assert len(full_content) > 0

    @pytest.mark.skip(reason="needs cache support")
    def test_list_models(self):

        # Test listing all models
        result = self.service.list_models()
        assert type(result)    is dict
        assert 'models' in result
        assert 'total'  in result
        assert result['total'] > 0

        models = result['models']
        assert type(models) is list

        # Check model structure
        if len(models) > 0:
            model = models[0]
            assert 'id'             in model
            assert 'name'           in model
            assert 'context_length' in model
            assert 'is_free'        in model
            assert 'pricing'        in model

    @pytest.mark.skip(reason="needs cache support")
    def test_list_models__filtered(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test listing only free models
        free_result = self.service.list_models(include_free = True, include_paid = False)
        free_models = free_result['models']

        # All should be free
        for model in free_models:
            assert model['is_free'] is True

        # Test listing only paid models
        paid_result = self.service.list_models(include_free = False, include_paid = True)
        paid_models = paid_result['models']

        # All should be paid
        for model in paid_models:
            assert model['is_free'] is False

    @pytest.mark.skip(reason="needs cache support")
    def test_estimate_cost(self):

        # Test cost estimation
        result = self.service.estimate_cost(
            model         = "openai/gpt-4o-mini",
            prompt_length = 1000,  # ~250 tokens
            max_tokens    = 100
        )

        assert type(result) is dict
        assert 'model'          in result
        assert 'estimated_cost' in result
        assert 'prompt_tokens'  in result
        assert 'max_tokens'     in result

        assert result['model']         == "openai/gpt-4o-mini"
        assert result['prompt_tokens'] == 250  # 1000 / 4
        assert result['max_tokens']    == 100

        # Check cost breakdown
        cost = result['estimated_cost']
        assert 'total_cost'   in cost
        assert 'prompt_cost'  in cost
        assert 'completion_cost' in cost

    @pytest.mark.skip(reason="needs cache support")
    def test_get_model_info(self):

        # Test getting info for a known model
        model_info = self.service.get_model_info("openai/gpt-4o-mini")

        assert type(model_info) is dict
        assert 'id'                   in model_info
        assert 'name'                 in model_info
        assert 'description'          in model_info
        assert 'context_length'       in model_info
        assert 'architecture'         in model_info
        assert 'pricing'              in model_info
        assert 'supported_parameters' in model_info

        # Check architecture structure
        arch = model_info['architecture']
        assert 'modality'          in arch
        assert 'tokenizer'         in arch
        assert 'input_modalities'  in arch
        assert 'output_modalities' in arch

    @pytest.mark.skip(reason="needs cache support")
    def test_get_model_info__not_found(self):

        # Test with non-existent model
        model_info = self.service.get_model_info("non-existent/model")
        assert model_info is None

    def test_chat_completion__with_provider(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test forcing a specific provider
        response = self.service.chat_completion(
            prompt   = "Say 'test'",
            model    = "openai/gpt-4o-mini",
            provider = "OpenAI",
            max_tokens = 10
        )

        assert 'choices' in response
        # Provider info might be in response if x_include_provider was true
        if 'provider' in response:
            assert response['provider'] == 'OpenAI'

    def test_chat_completion__with_max_cost(self):

        # Test with max cost limit
        response = self.service.chat_completion(
            prompt    = "Say 'test'",
            model     = "mistralai/mistral-small-3.2-24b-instruct:free",
            max_cost  = 0.001,  # Very low cost limit
            max_tokens = 5
        )

        # Should still work with free model
        assert 'choices' in response

    @pytest.mark.skip(reason="needs cache support")
    def test_chat_completion_stream__with_system_prompt(self):

        chunks = []
        for chunk in self.service.chat_completion_stream(
            prompt        = "What format should you use?",
            model         = "mistralai/mistral-small-3.2-24b-instruct:free",
            system_prompt = "Always respond in JSON format",
            temperature   = 0.1,
            max_tokens    = 30
        ):
            chunks.append(chunk)

        assert len(chunks) > 0

        # Collect full response
        full_content = ""
        for chunk in chunks:
            if 'choices' in chunk and len(chunk['choices']) > 0:
                delta = chunk['choices'][0].get('delta', {})
                if 'content' in delta:
                    full_content += delta['content']

        # Response should be influenced by system prompt
        assert len(full_content) > 0