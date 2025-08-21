import pytest
import json
from unittest                                                                                        import TestCase
from fastapi                                                                                         import HTTPException
from fastapi.responses                                                                               import StreamingResponse
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.utils.Env                                                                           import get_env, load_dotenv
from osbot_utils.utils.Objects                                                                       import base_classes
from osbot_fast_api.api.routes.Fast_API__Routes                                                      import Fast_API__Routes
from mgraph_ai_service_llms.platforms.open_router.fast_api.routes.Routes__Open_Router                import Routes__Open_Router
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                       import Service__Open_Router, ENV_NAME_OPEN_ROUTER__API_KEY
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers        import Schema__Open_Router__Providers
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Supported_Models import Schema__Open_Router__Supported_Models
from tests.unit.Service__Fast_API__Test_Objs import setup__service_fast_api_test_objs


class test_Routes__Open_Router(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip("No Open_Router API key set")
        setup__service_fast_api_test_objs()
        cls.routes = Routes__Open_Router()

    def test__init__(self):
        with self.routes as _:
            assert type(_)               is Routes__Open_Router
            assert base_classes(_)       == [Fast_API__Routes, Type_Safe, object]
            assert _.tag                 == 'chat'
            assert type(_.open_router)   is Service__Open_Router

    def test_complete__with_actual_api(self):
        # if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
        #     pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test basic completion
        result = self.routes.complete(
            prompt      = "Reply with 'success' only",
            model       = Schema__Open_Router__Supported_Models.Mistral_AI__Mistral_Small__Free,
            temperature = 0.1,
            max_tokens  = 10
        )

        # Verify result structure
        assert type(result) is dict
        assert result['status']   == 'success'
        assert result['model']    == Schema__Open_Router__Supported_Models.Mistral_AI__Mistral_Small__Free.value
        assert 'provider' in result
        assert 'response' in result
        assert 'usage'    in result
        assert 'cost'     in result

        # Check response content
        assert len(result['response']) > 0

        # Check usage stats
        usage = result['usage']
        assert 'prompt_tokens'     in usage
        assert 'completion_tokens' in usage
        assert 'total_tokens'      in usage

    def test_complete__with_system_prompt(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        result = self.routes.complete(
            prompt        = "What is 2+2?",
            model         = Schema__Open_Router__Supported_Models.Mistral_AI__Mistral_Small__Free,
            system_prompt = "You are a math tutor. Always explain your reasoning.",
            temperature   = 0.1,
            max_tokens    = 50
        )

        assert result['status'] == 'success'
        assert len(result['response']) > 0
        # Response should show reasoning due to system prompt

    @pytest.mark.skip(reason="todo: find root cause of bug")
    def test_complete__with_provider(self):

        result = self.routes.complete(
            prompt   = "Say 'test'",
            model    = Schema__Open_Router__Supported_Models.Open_AI__GPT_4o_Mini,
            provider = Schema__Open_Router__Providers.AUTO,
            max_tokens = 10
        )

        assert result['status'] == 'success'
        assert 'provider' in result

    def test_complete__with_max_cost(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        result = self.routes.complete(
            prompt    = "Say 'hi'",
            model     = Schema__Open_Router__Supported_Models.Mistral_AI__Mistral_Small__Free,
            max_cost  = 0.001,
            max_tokens = 5
        )

        assert result['status'] == 'success'
        # Should work with free model regardless of cost limit

    def test_complete__error_handling(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            # Test error when no API key
            with self.assertRaises(HTTPException) as context:
                self.routes.complete(
                    prompt = "test",
                    model  = Schema__Open_Router__Supported_Models.Mistral_AI__Mistral_Small__Free
                )
            assert context.exception.status_code == 400
            assert "API key not found" in context.exception.detail

    @pytest.mark.skip(reason="Test needs fixing")
    def test_complete_stream__with_actual_api(self):

        # Get streaming response
        response = self.routes.complete_stream(
            prompt      = "Count to 3",
            model       = Schema__Open_Router__Supported_Models.Mistral_AI__Mistral_Small__Free,
            temperature = 0.1,
            max_tokens  = 20
        )

        # Verify response type
        assert type(response) is StreamingResponse
        assert response.media_type == "text/event-stream"

        # Collect streamed data
        chunks = []
        for chunk in response.body_iterator:
            chunks.append(chunk)

        # Should have received chunks
        assert len(chunks) > 0

        # Parse and verify chunks
        content_received = False
        for chunk in chunks:
            if chunk.startswith('data: '):
                data_str = chunk[6:]
                if data_str.strip() == '[DONE]':
                    break
                try:
                    data = json.loads(data_str)
                    if 'choices' in data:
                        content_received = True
                except json.JSONDecodeError:
                    pass

        assert content_received

    @pytest.mark.skip(reason="Test needs fixing")
    def test_complete_stream__with_system_prompt(self):

        response = self.routes.complete_stream(
            prompt        = "What format should I use?",
            model         = Schema__Open_Router__Supported_Models.Mistral_AI__Mistral_Small__Free,
            system_prompt = "Always suggest JSON format",
            temperature   = 0.1,
            max_tokens    = 30
        )

        assert type(response) is StreamingResponse

        # Collect content
        full_content = ""
        for chunk in response.body_iterator:
            if chunk.startswith('data: '):
                data_str = chunk[6:]
                if data_str.strip() != '[DONE]':
                    try:
                        data = json.loads(data_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                full_content += delta['content']
                    except:
                        pass

        assert len(full_content) > 0

    def test_models(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test getting all models
        result = self.routes.models()

        assert type(result) is dict
        assert 'models' in result
        assert 'total'  in result

        models = result['models']
        assert type(models) is list
        assert result['total'] == len(models)

        if len(models) > 0:
            model = models[0]
            assert 'id'             in model
            assert 'name'           in model
            assert 'context_length' in model
            assert 'is_free'        in model
            assert 'pricing'        in model

    def test_models__filtered(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test free models only
        free_result = self.routes.models(include_free = True, include_paid = False)
        for model in free_result['models']:
            assert model['is_free'] is True

        # Test paid models only
        paid_result = self.routes.models(include_free = False, include_paid = True)
        for model in paid_result['models']:
            assert model['is_free'] is False

        # Test no models (exclude both)
        no_result = self.routes.models(include_free = False, include_paid = False)
        assert no_result['total']  == 0
        assert no_result['models'] == []

    def test_model_info(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test with valid model
        result = self.routes.model_info("openai/gpt-4o-mini")

        assert type(result) is dict
        assert result['id'] == "openai/gpt-4o-mini"
        assert 'name'                 in result
        assert 'description'          in result
        assert 'context_length'       in result
        assert 'architecture'         in result
        assert 'pricing'              in result
        assert 'supported_parameters' in result

    def test_model_info__not_found(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test with non-existent model
        with self.assertRaises(HTTPException) as context:
            self.routes.model_info("non-existent/model")

        assert context.exception.status_code == 404
        assert "Model not found" in context.exception.detail

    def test_estimate_cost(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        result = self.routes.estimate_cost(
            model         = Schema__Open_Router__Supported_Models.Open_AI__GPT_4o_Mini,
            prompt_length = 1000,
            max_tokens    = 100
        )

        assert type(result) is dict
        assert 'model'          in result
        assert 'estimated_cost' in result
        assert 'prompt_tokens'  in result
        assert 'max_tokens'     in result

        assert result['model']         == Schema__Open_Router__Supported_Models.Open_AI__GPT_4o_Mini.value
        assert result['prompt_tokens'] == 250  # 1000 / 4
        assert result['max_tokens']    == 100

        cost = result['estimated_cost']
        assert 'total_cost' in cost
        assert 'model'      in cost

    def test_estimate_cost__invalid_model(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Using a free model that might not have pricing info
        # This should handle the error gracefully
        with self.assertRaises(HTTPException) as context:
            # Create a fake model that doesn't exist
            fake_model = type('obj', (object,), {'value': 'fake/non-existent-model'})()
            self.routes.estimate_cost(
                model         = fake_model,
                prompt_length = 100,
                max_tokens    = 10
            )

        assert context.exception.status_code == 400

    def test_providers(self):
        result = self.routes.providers()

        assert type(result) is dict
        assert 'providers' in result

        providers = result['providers']
        assert type(providers) is list
        assert len(providers) == len(Schema__Open_Router__Providers)

        # Check each provider
        for provider in providers:
            assert 'id'           in provider
            assert 'name'         in provider
            assert 'header_value' in provider

        # Check specific providers
        provider_ids = [p['id'] for p in providers]
        assert 'auto'      in provider_ids
        assert 'cerebras'  in provider_ids
        assert 'groq'      in provider_ids
        assert 'together'  in provider_ids
        assert 'deepinfra' in provider_ids

    def test_setup_routes(self):
        # Create fresh instance to test route setup
        routes = Routes__Open_Router()

        # Manually call setup_routes
        routes.setup_routes()

        # The routes should be added to the router
        # Note: We can't easily test the actual FastAPI router without a full app context
        # but we can verify the method runs without error
        assert True  # If we get here, setup_routes worked

    @pytest.mark.skip(reason="todo: find root cause of bug")
    def test_complete__with_all_parameters(self):
        # if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
        #     pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        # Test with all optional parameters
        result = self.routes.complete(
            prompt        = "Reply with OK",
            model         = Schema__Open_Router__Supported_Models.Mistral_AI__Mistral_Small__Free,
            system_prompt = "Be brief",
            temperature   = 0.5,
            max_tokens    = 5,
            provider      = Schema__Open_Router__Providers.AUTO,
            max_cost      = 0.01
        )

        assert result['status'] == 'success'
        assert len(result['response']) > 0

    def test_complete_stream__error_handling(self):
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            # Should handle missing API key gracefully
            response = self.routes.complete_stream(
                prompt = "test",
                model  = Schema__Open_Router__Supported_Models.Mistral_AI__Mistral_Small__Free
            )

            # Should return streaming response even with error
            assert type(response) is StreamingResponse

            # Collect error from stream
            for chunk in response.body_iterator:
                if chunk.startswith('data: '):
                    data_str = chunk[6:]
                    if data_str.strip() != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            if 'error' in data:
                                assert data['type'] == 'stream_error'
                                break
                        except:
                            pass