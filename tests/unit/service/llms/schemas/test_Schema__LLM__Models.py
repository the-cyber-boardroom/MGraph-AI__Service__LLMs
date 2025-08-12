from unittest                                                   import TestCase
from enum                                                       import Enum
from mgraph_ai_service_llms.service.schemas.Schema__LLM__Models import Schema__LLM__Models


class test_Schema__LLM__Models(TestCase):

    def test__enum_values(self):
        assert issubclass(Schema__LLM__Models, Enum)

        # Check all models are defined
        model_names = [model.name for model in Schema__LLM__Models]
        expected_names = [
            'MISTRAL_SMALL_FREE',
            'MOONSHOT_KIMI_FREE',
            'QWEN_235B_FREE'    ,
            'DEEPSEEK_FREE'     ,
            'GEMINI_2_FLASH'    ,
            'GPT_4O_MINI'       ,
            'GPT_4_1_MINI'      ,
            'GPT_OSS_120B'      ,
            'GPT_OSS_20B'       ,
        ]
        assert model_names == expected_names

    def test__model_values(self):
        # Test each model's value
        assert Schema__LLM__Models.MISTRAL_SMALL_FREE.value == "mistralai/mistral-small-3.2-24b-instruct:free"
        assert Schema__LLM__Models.MOONSHOT_KIMI_FREE.value == "moonshotai/kimi-k2:free"
        assert Schema__LLM__Models.QWEN_235B_FREE.value     == "qwen/qwen3-235b-a22b-07-25:free"
        assert Schema__LLM__Models.DEEPSEEK_FREE.value      == "tngtech/deepseek-r1t2-chimera:free"
        assert Schema__LLM__Models.GEMINI_2_FLASH.value     == "google/gemini-2.0-flash-lite-001"
        assert Schema__LLM__Models.GPT_4O_MINI.value        == "openai/gpt-4o-mini"
        assert Schema__LLM__Models.GPT_4_1_MINI.value       == "openai/gpt-4.1-mini"

    def test__is_free_property(self):
        # Test free models
        free_models = [
            Schema__LLM__Models.MISTRAL_SMALL_FREE,
            Schema__LLM__Models.MOONSHOT_KIMI_FREE,
            Schema__LLM__Models.QWEN_235B_FREE,
            Schema__LLM__Models.DEEPSEEK_FREE
        ]

        for model in free_models:
            assert model.is_free is True
            assert "free" in model.value

        # Test paid models
        paid_models = [
            Schema__LLM__Models.GEMINI_2_FLASH,
            Schema__LLM__Models.GPT_4O_MINI,
            Schema__LLM__Models.GPT_4_1_MINI
        ]

        for model in paid_models:
            assert model.is_free is False
            assert "free" not in model.value

    def test__provider_property(self):
        test_cases = [
            (Schema__LLM__Models.MISTRAL_SMALL_FREE, "mistralai"),
            (Schema__LLM__Models.MOONSHOT_KIMI_FREE, "moonshotai"),
            (Schema__LLM__Models.QWEN_235B_FREE,     "qwen"),
            (Schema__LLM__Models.DEEPSEEK_FREE,      "tngtech"),
            (Schema__LLM__Models.GEMINI_2_FLASH,     "google"),
            (Schema__LLM__Models.GPT_4O_MINI,        "openai"),
            (Schema__LLM__Models.GPT_4_1_MINI,       "openai"),
        ]

        for model, expected_provider in test_cases:
            assert model.provider == expected_provider

    def test__all_models_count(self):
        all_models = list(Schema__LLM__Models)
        assert len(all_models) == 9

        # Count free vs paid
        free_count = sum(1 for m in all_models if m.is_free)
        paid_count = sum(1 for m in all_models if not m.is_free)

        assert free_count == 4
        assert paid_count == 5
        assert free_count + paid_count == len(all_models)
