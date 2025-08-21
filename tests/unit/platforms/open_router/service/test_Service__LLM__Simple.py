import pytest
from unittest                                                                                                import TestCase
from osbot_utils.type_safe.Type_Safe                                                                         import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                                      import Safe_Str
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects                                                                               import base_classes
from osbot_utils.utils.Env                                                                                   import get_env, load_dotenv
from mgraph_ai_service_llms.platforms.open_router.service.Service__LLM__Simple import Service__LLM__Simple, HIGH_THROUGHPUT_MODELS
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                               import Service__Open_Router, ENV_NAME_OPEN_ROUTER__API_KEY
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Provider_Preferences  import Schema__Open_Router__Provider_Preferences
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers                import Schema__Open_Router__Providers
from tests.unit.Service__Fast_API__Test_Objs                                                                 import setup__service_fast_api_test_objs


class test_Service__LLM__Simple(TestCase):

    @classmethod
    def setUpClass(cls):                                                                                     # Setup for all tests
        load_dotenv()
        setup__service_fast_api_test_objs()

        if not get_env(ENV_NAME_OPEN_ROUTER__API_KEY):
            pytest.skip(f"Skipping test: OpenRouter API key not found in environment variable: {ENV_NAME_OPEN_ROUTER__API_KEY}")

        cls.service = Service__LLM__Simple()

    def test__init__(self):                                                                                  # Test initialization
        service = Service__LLM__Simple()

        assert type(service)             is Service__LLM__Simple
        assert base_classes(service)     == [Type_Safe, object]
        assert type(service.open_router) is Service__Open_Router

    def test_high_throughput_models_constant(self):                                                          # Test model constants
        assert HIGH_THROUGHPUT_MODELS == { "gpt-oss-120b" : "openai/gpt-oss-120b"              ,
                                           "gpt-oss-20b"  : "openai/gpt-oss-20b"               ,
                                           "gpt-5-nano"   : "openai/gpt-5-nano"                ,
                                           "gpt-5-mini"   : "openai/gpt-5-mini"                ,
                                           "gemini-2"     : "google/gemini-2.0-flash-lite-001" }

    def test_execute_completion_basic(self):                                                                 # Test basic completion with real API
        result = self.service.execute_completion(user_prompt   = "Reply with 'test' only"              ,
                                                 system_prompt = "You are a test bot. Reply concisely.")

        assert "duration_seconds" in result
        assert "model_used"       in result
        assert "provider_used"    in result
        assert "response_text"    in result

        assert result["model_used"]          == "openai/gpt-oss-120b"
        assert type(result["duration_seconds"]) is float
        assert result["duration_seconds"]      > 0
        assert len(result["response_text"])    > 0

    def test_execute_completion_with_groq_provider(self):                                                    # Test with Groq provider
        result = self.service.execute_completion(user_prompt   = "Say 'hello'"                         ,
                                                 provider_name = Schema__Open_Router__Providers.GROQ   )

        assert result["model_used"]         == "openai/gpt-oss-120b"
        assert "provider_used"              in result
        assert len(result["response_text"]) > 0
        assert result["provider_used"]      == "Groq"

    def test_execute_completion_with_cerebras_provider(self):                                                # Test with Cerebras provider
        result = self.service.execute_completion(user_prompt   = "Count to 3"                               ,
                                                 system_prompt = "Count simply"                             ,
                                                 provider_name = Schema__Open_Router__Providers.CEREBRAS    )

        assert result["model_used"] == "openai/gpt-oss-120b"
        assert len(result["response_text"]) > 0

    def test_execute_completion_different_model_gpt5_nano(self):                                             # Test with gpt-5-nano model
        result = self.service.execute_completion(user_prompt = "What is 2+2?"       ,
                                                 model_key   = "gpt-5-nano"        )

        assert result["model_used"] == "openai/gpt-5-nano"
        assert "4" in result["response_text"] or "four" in result["response_text"].lower()

    @pytest.mark.skip(reason="gpt-5-mini might have higher costs")
    def test_execute_completion_different_model_gpt5_mini(self):                                             # Test with gpt-5-mini model
        result = self.service.execute_completion(user_prompt = "Define AI in 5 words" ,
                                                 model_key   = "gpt-5-mini"           )

        assert result["model_used"] == "openai/gpt-5-mini"
        assert len(result["response_text"]) > 0

    def test_execute_completion_invalid_model(self):                                                         # Test invalid model key
        with pytest.raises(ValueError) as exc_info:
            self.service.execute_completion(user_prompt = "Test"          ,
                                           model_key   = "invalid-model"  )

        assert "Invalid model key: invalid-model" in str(exc_info.value)
        assert "Valid options:" in str(exc_info.value)

    # def test_execute_completion_with_preferences(self):                                                      # Test with provider preferences
    #     preferences = Schema__Open_Router__Provider_Preferences(
    #         order           = [Safe_Str("groq"), Safe_Str("cerebras")] ,
    #         allow_fallbacks = True                                     ,
    #         data_collection = "deny"                                   )
    #
    #     result = self.service.execute_completion_with_preferences(
    #         user_prompt          = "What is Python?"                   ,
    #         system_prompt        = "Give a one-sentence definition"    ,
    #         model_key            = "gpt-oss-20b"                       ,
    #         provider_preferences = preferences                         )
    #
    #     assert result["duration_seconds"]     > 0
    #     assert result["model_used"]           == "openai/gpt-oss-20b"
    #     assert result["provider_requested"]   == "groq"                                                      # First in order
    #     assert "provider_used" in result
    #     assert "provider_preferences" in result
    #     assert result["provider_preferences"]["order"]           == ["groq", "cerebras"]
    #     assert result["provider_preferences"]["allow_fallbacks"] == True
    #     assert len(result["response_text"])   > 0
    #     assert "python" in result["response_text"].lower() or "programming" in result["response_text"].lower()

    # def test_execute_completion_with_preferences_no_order(self):                                             # Test preferences without order
    #     preferences = Schema__Open_Router__Provider_Preferences(
    #         allow_fallbacks     = False                                      ,
    #         ignore_providers    = [Safe_Str("openai"), Safe_Str("anthropic")])
    #
    #     result = self.service.execute_completion_with_preferences(
    #         user_prompt          = "Say 'ok'"      ,
    #         provider_preferences = preferences     )
    #
    #     assert result["provider_requested"]  is None                                                         # No order specified
    #     assert result["model_used"]          == "openai/gpt-oss-120b"
    #     assert len(result["response_text"])  > 0

    def test_execute_completion_timing_precision(self):                                                      # Test timing precision
        result = self.service.execute_completion(user_prompt = "Reply quickly with 'done'")

        assert type(result["duration_seconds"]) is float
        assert result["duration_seconds"] > 0
        assert result["duration_seconds"] < 60                                                               # Should complete within 60 seconds

        # Check that it's rounded to 3 decimal places
        duration_str = str(result["duration_seconds"])
        if '.' in duration_str:
            decimal_places = len(duration_str.split('.')[1])
            assert decimal_places <= 3

    def test_all_models_valid(self):                                                                         # Test that all model keys work
        # Only test with cheap/free models to avoid costs
        test_models = ["gpt-oss-120b", "gpt-oss-20b", "gpt-5-nano"]

        for model_key in test_models:
            result = self.service.execute_completion(user_prompt = f"Say '{model_key}'"  ,
                                                     model_key   = model_key             )

            assert result["model_used"] == HIGH_THROUGHPUT_MODELS[model_key]
            assert len(result["response_text"]) > 0

    # def test_provider_enum_values(self):                                                                     # Test different provider enums
    #     # Test with AUTO provider which should always work
    #     result = self.service.execute_completion(user_prompt   = "What is 1+1?"                    ,
    #                                              provider_name = Schema__Open_Router__Providers.AUTO)
    #
    #     assert result["model_used"]         == "openai/gpt-oss-120b"
    #     assert len(result["response_text"]) > 0
    #     assert "2" in result["response_text"] or "two" in result["response_text"].lower()

    # def test_execute_completion_with_long_prompt(self):                                                      # Test with longer prompt
    #     long_prompt = "List three colors. " * 10                                                             # Repeat to make it longer
    #
    #     result = self.service.execute_completion(user_prompt   = long_prompt                  ,
    #                                              system_prompt = "Be extremely concise"      )
    #
    #     assert result["model_used"]         == "openai/gpt-oss-120b"
    #     assert len(result["response_text"]) > 0
    #     assert result["duration_seconds"]   > 0
    #
    # def test_execute_completion_response_consistency(self):                                                  # Test response consistency
    #     # Make the same request twice to check caching behavior
    #     prompt = "What is the capital of France?"
    #
    #     result1 = self.service.execute_completion(user_prompt = prompt)
    #     result2 = self.service.execute_completion(user_prompt = prompt)
    #
    #     assert result1["model_used"] == result2["model_used"]
    #     assert "paris" in result1["response_text"].lower()
    #     assert "paris" in result2["response_text"].lower()
    #
    #     # Second call might be faster due to caching
    #     if result2["duration_seconds"] < result1["duration_seconds"]:
    #         print(f"Cache hit detected: {result1['duration_seconds']}s vs {result2['duration_seconds']}s")
    #
    # def test_execute_completion_gemini_model(self):                                                          # Test with Gemini model
    #     result = self.service.execute_completion(user_prompt = "What is water?"  ,
    #                                              model_key   = "gemini-2"        )
    #
    #     assert result["model_used"] == "google/gemini-2.0-flash-lite-001"
    #     assert len(result["response_text"]) > 0
    #     assert "h2o" in result["response_text"].lower() or "hydrogen" in result["response_text"].lower() or "liquid" in result["response_text"].lower()