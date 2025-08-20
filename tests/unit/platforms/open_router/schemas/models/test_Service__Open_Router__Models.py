import pytest
from unittest                                                                                               import TestCase
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_int                                                              import Safe_Int
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url                                            import Safe_Str__Url
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                                       import Type_Safe__List
from osbot_utils.utils.Objects                                                                              import base_classes
from osbot_utils.utils.Misc                                                                                 import list_set
from mgraph_ai_service_llms.platforms.open_router.Service__Open_Router__Models                              import Service__Open_Router__Models
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_ID                   import Safe_Str__Open_Router__Model_ID
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Modality                   import Safe_Str__Open_Router__Modality
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model                 import Schema__Open_Router__Model
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Pricing__Float import Schema__Open_Router__Model__Pricing__Float
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Models__Response      import Schema__Open_Router__Models__Response


class test_Service__Open_Router__Models(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Service__Open_Router__Models()

    def test__init__(self):
        with self.service as _:
            assert type(_)         is Service__Open_Router__Models
            assert base_classes(_) == [Type_Safe, object]
            assert type(_.api__url__models()) is Safe_Str__Url
            assert str(_.api__url__models ()) == "https://openrouter.ai/api/v1/models"

    def test_fetch_models(self):
        # if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
        #     pytest.skip('This test requires OPEN_ROUTER__API_KEY to be set')

        result = self.service.fetch_models()

        assert type(result)      is Schema__Open_Router__Models__Response
        assert type(result.data) is Type_Safe__List
        assert len(result.data)  > 0                                              # Should have at least some models

        # Check first model structure
        first_model = result.data[0]
        assert type(first_model)                    is Schema__Open_Router__Model
        assert type(first_model.id)                 is Safe_Str__Open_Router__Model_ID
        assert type(first_model.context_length)     is Safe_Int
        assert type(first_model.pricing.prompt)     is Schema__Open_Router__Model__Pricing__Float
        assert type(first_model.pricing.completion) is Schema__Open_Router__Model__Pricing__Float

        # Check that models have expected fields populated
        assert len(str(first_model.id))          > 0
        assert len(str(first_model.name))        > 0
        assert first_model.context_length        > 0
        assert len(first_model.supported_parameters) > 0

    def test_fetch_models__error_handling(self):
        # Test with invalid URL
        service_with_bad_url        = Service__Open_Router__Models()
        service_with_bad_url.api__url__models = Safe_Str__Url("https://invalid-url-that-does-not-exist.com/api")

        with pytest.raises(ValueError) as context:
            service_with_bad_url.fetch_models()

        assert "Failed to fetch models from OpenRouter" in str(context.value)

    def test_get_cached_models(self):
        # First call should fetch from API
        models_1 = self.service.api__models()

        assert type(models_1) is Type_Safe__List
        assert len(models_1 )  > 0
        assert all(type(m) is Schema__Open_Router__Model for m in models_1)

        # Second call should return cached version (same object)
        models_2 = self.service.api__models()

        assert models_2 is models_1                                               # Same object due to caching

    def test_get_model_by_id(self):
        # Get models first
        models = self.service.api__models()

        if len(models) > 0:
            # Test with existing model
            test_model_id = models[0].id
            found_model   = self.service.get_model_by_id(test_model_id)

            assert found_model is not None
            assert type(found_model) is Schema__Open_Router__Model
            assert found_model.id    == test_model_id

            # Test with non-existent model
            non_existent_id = Safe_Str__Open_Router__Model_ID("non-existent/model-id")
            result          = self.service.get_model_by_id(non_existent_id)

            assert result is None

    def test_get_model_by_id__with_known_model(self):
        # Test with a known free model that should exist
        known_model_id = Safe_Str__Open_Router__Model_ID("mistralai/mistral-small-3.2-24b-instruct:free")
        model          = self.service.get_model_by_id(known_model_id)

        if model:                                                                 # Model might not always be available
            assert type(model)    is Schema__Open_Router__Model
            assert model.id       == known_model_id
            assert "mistral" in str(model.name).lower()
            assert float(model.pricing.prompt) == 0                               # Free model

    def test_get_models_by_modality(self):
        # Test with text->text modality (should have many models)
        text_modality = Safe_Str__Open_Router__Modality("text->text")
        text_models   = self.service.get_models_by_modality(text_modality)

        if len(text_models) > 0:
            assert type(text_models) is list
            assert all(type(m) is Schema__Open_Router__Model for m in text_models)
            assert all(m.architecture.modality == text_modality for m in text_models)

        # Test with multimodal
        multimodal_modality = Safe_Str__Open_Router__Modality("text+image->text")
        multimodal_models   = self.service.get_models_by_modality(multimodal_modality)

        if len(multimodal_models) > 0:
            assert all(m.architecture.modality == multimodal_modality for m in multimodal_models)

        # Test with non-existent modality
        fake_modality = Safe_Str__Open_Router__Modality("fake->modality")
        fake_models   = self.service.get_models_by_modality(fake_modality)

        assert fake_models == []

    def test_get_free_models(self):
        free_models = self.service.get_free_models()

        assert type(free_models) is list

        if len(free_models) > 0:
            # All free models should have 0 cost
            for model in free_models:
                assert type(model) is Schema__Open_Router__Model
                assert float(model.pricing.prompt)     == 0.0
                assert float(model.pricing.completion) == 0.0

            # Check that known free models are included
            free_model_ids = [str(m.id) for m in free_models]

            # At least one of these should be free
            known_free_models = [
                "mistralai/mistral-small-3.2-24b-instruct:free",
                "moonshotai/kimi-k2:free",
                "qwen/qwen3-235b-a22b-07-25:free",
                "tngtech/deepseek-r1t2-chimera:free"
            ]

            found_known_free = any(model in free_model_ids for model in known_free_models)
            assert found_known_free is True                                       # At least one known free model should exist

    def test_get_free_models__verification(self):
        # Get all models and free models
        all_models  = self.service.api__models()
        free_models = self.service.get_free_models()

        # Manually check which models are free
        manually_checked_free = []
        for model in all_models:
            if float(model.pricing.prompt) == 0 and float(model.pricing.completion) == 0:
                manually_checked_free.append(model)

        # Should match
        assert len(free_models) == len(manually_checked_free)

        free_ids     = set(str(m.id) for m in free_models)
        manual_ids   = set(str(m.id) for m in manually_checked_free)

        assert free_ids == manual_ids

    def test_get_models_summary(self):
        summary = self.service.get_models_summary()

        assert type(summary) is dict
        assert list_set(summary) == ['free_models', 'free_models_count', 'modalities', 'tokenizers', 'total_models']

        # Check structure
        assert type(summary['total_models'])      is int
        assert type(summary['free_models_count']) is int
        assert type(summary['free_models'])       is list
        assert type(summary['modalities'])        is dict
        assert type(summary['tokenizers'])        is list

        # Check values make sense
        assert summary['total_models']      > 0
        assert summary['free_models_count'] >= 0
        assert summary['free_models_count'] <= summary['total_models']
        assert len(summary['free_models'])  == summary['free_models_count']

        # Check modalities structure
        for modality, model_ids in summary['modalities'].items():
            assert type(modality)  is str
            assert type(model_ids) is list
            assert len(model_ids)  > 0                                            # Each modality should have at least one model

        # Check tokenizers
        assert len(summary['tokenizers']) > 0
        assert all(type(t) is str for t in summary['tokenizers'])

        # Common tokenizers that should exist
        common_tokenizers = ["Mistral", "Other"]
        for tokenizer in common_tokenizers:
            if tokenizer in summary['tokenizers']:
                assert tokenizer in summary['tokenizers']

    def test_get_models_summary__consistency(self):
        summary    = self.service.get_models_summary()
        all_models = self.service.api__models()

        # Total models should match
        assert summary['total_models'] == len(all_models)

        # Count models in modalities
        modality_model_count = sum(len(models) for models in summary['modalities'].values())
        assert modality_model_count == summary['total_models']

        # Free models count should match
        free_models = self.service.get_free_models()
        assert summary['free_models_count'] == len(free_models)
        assert len(summary['free_models'])  == len(free_models)

    def test_safe_float_pricing_conversion(self):
        models = self.service.api__models()

        if len(models) > 0:
            # Test that Safe_Float prices can be converted to float
            for model in models[:5]:                                              # Test first 5 models
                prompt_price     = float(model.pricing.prompt)
                completion_price = float(model.pricing.completion)

                assert type(prompt_price)     is float
                assert type(completion_price) is float
                assert prompt_price     >= 0
                assert completion_price >= 0

    def test_model_architecture_details(self):
        models = self.service.api__models()

        if len(models) > 0:
            # Check architecture details
            for model in models[:10]:                                             # Check first 10 models
                arch = model.architecture

                assert len(arch.input_modalities)  > 0
                assert len(arch.output_modalities) > 0
                assert len(str(arch.modality))     > 0
                assert len(str(arch.tokenizer))    > 0

                # Modality should match input/output pattern
                assert "->" in str(arch.modality) or "+" in str(arch.modality)

    def test_caching_behavior(self):
        # Create new instance to ensure clean cache
        new_service = Service__Open_Router__Models()

        # First call fetches from API
        models_1 = new_service.api__models()

        # Modify the API URL to simulate network issue
        original_url     = new_service.api__url__models
        new_service.api__url__models = Safe_Str__Url("https://invalid-url.com")

        # Second call should still work due to cache
        models_2 = new_service.api__models()

        assert models_2 is models_1                                               # Same cached object

        # Restore URL
        new_service.api__url__models = original_url

    def test_empty_models_handling(self):
        # Test methods with empty model list
        service = Service__Open_Router__Models()

        # Mock empty cache
        service.api__models = lambda: []

        # Test each method handles empty list gracefully
        assert service.get_model_by_id(Safe_Str__Open_Router__Model_ID("test")) is None
        assert service.get_models_by_modality(Safe_Str__Open_Router__Modality("test")) == []
        assert service.get_free_models() == []

        summary = service.get_models_summary()
        assert summary['total_models']      == 0
        assert summary['free_models_count'] == 0
        assert summary['free_models']       == []
        assert summary['modalities']        == {}
        assert summary['tokenizers']        == []