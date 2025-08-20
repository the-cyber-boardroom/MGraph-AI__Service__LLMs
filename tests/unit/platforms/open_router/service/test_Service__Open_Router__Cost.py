# tests/unit/platforms/open_router/test_Service__Open_Router__Cost.py

from unittest                                                                             import TestCase
from unittest.mock                                                                        import Mock, patch

import pytest
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.type_safe.primitives.safe_float.Safe_Float import Safe_Float
from osbot_utils.utils.Objects                                                            import base_classes

from mgraph_ai_service_llms.platforms.open_router.schemas.cost.Schema__Open_Router__Cost_Breakdown           import Schema__Open_Router__Cost_Breakdown
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model                  import Schema__Open_Router__Model
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Pricing         import Schema__Open_Router__Model__Pricing
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Pricing__Float  import Schema__Open_Router__Model__Pricing__Float
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router__Cost                         import Service__Open_Router__Cost


class test_Service__Open_Router__Cost(TestCase):

    @classmethod
    def setUpClass(cls):        # Setup test service with mocked models
        cls.cost_service = Service__Open_Router__Cost()

        # Create mock pricing for testing
        cls.mock_pricing = Schema__Open_Router__Model__Pricing(prompt             = Schema__Open_Router__Model__Pricing__Float(0.15 ),  # $0.15 per million tokens
                                                               completion         = Schema__Open_Router__Model__Pricing__Float(0.60 ),  # $0.60 per million tokens
                                                               request            = Schema__Open_Router__Model__Pricing__Float(0.0  ),
                                                               image              = Schema__Open_Router__Model__Pricing__Float(0.01 ),  # $0.01 per image
                                                               input_cache_read   = Schema__Open_Router__Model__Pricing__Float(0.075), # $0.075 per million cached tokens
                                                               input_cache_write  = Schema__Open_Router__Model__Pricing__Float(0.15 ))  # $0.15 per million tokens

        cls.free_pricing = Schema__Open_Router__Model__Pricing(prompt     = Schema__Open_Router__Model__Pricing__Float(0.0),
                                                               completion = Schema__Open_Router__Model__Pricing__Float(0.0))

    def test_setUpClass(self):                          # Verify class setup and inheritance
        with self.cost_service as _:
            assert type(_)          is Service__Open_Router__Cost
            assert base_classes(_)  == [Type_Safe, object]
            assert _.models_service is not None

    def test__calculate_token_cost(self):       # Test token cost calculation
        # Test normal calculation
        cost = self.cost_service._calculate_token_cost(1000, 0.15)  # 1000 tokens at $0.15/million
        assert cost == Safe_Float("0.00015")

        # Test with larger numbers
        cost = self.cost_service._calculate_token_cost(1000000, 0.60)  # 1 million tokens at $0.60/million
        assert cost == Safe_Float("0.60")

        # Test with zero tokens
        cost = self.cost_service._calculate_token_cost(0, 0.15)
        assert cost == Safe_Float("0")

        # Test with None price
        cost = self.cost_service._calculate_token_cost(1000, None)
        assert cost == Safe_Float("0")

    def test__calculate_from_pricing__basic(self):  # Test basic cost calculation from pricing
        usage = { "prompt_tokens"     : 1000 ,
                  "completion_tokens" : 500  ,
                  "total_tokens"      : 1500 }

        breakdown = self.cost_service._calculate_from_pricing(pricing  = self.mock_pricing,
                                                              usage    = usage            ,
                                                              model_id = "test/model"     ,
                                                              provider = "openai"         )

        assert breakdown.prompt_tokens      == 1000
        assert breakdown.completion_tokens  == 500
        assert breakdown.total_tokens       == 1500
        assert breakdown.prompt_cost        == Safe_Float("0.00015")      # 1000 * 0.15/1M
        assert breakdown.completion_cost    == Safe_Float("0.0003")   # 500 * 0.60/1M
        assert breakdown.total_cost         == Safe_Float("0.00045")       # 0.00015 + 0.0003
        assert breakdown.model_id           == "test/model"
        assert breakdown.provider           == "openai"

        # Check cost per 1k tokens
        expected_per_1k = (Safe_Float("0.00045") / Safe_Float("1500")) * Safe_Float("1000")
        assert breakdown.cost_per_1k_tokens == expected_per_1k

    def test__calculate_from_pricing__with_cache(self):         # Test calculation with cache hits
        usage = {
            "prompt_tokens"            : 800,   # Non-cached prompt tokens
            "completion_tokens"        : 500,
            "total_tokens"             : 1500,
            "prompt_cache_hit_tokens"  : 200,   # Cached tokens (cheaper)
            "prompt_cache_miss_tokens" : 800,   # Cache write
        }

        breakdown = self.cost_service._calculate_from_pricing(
            pricing  = self.mock_pricing,
            usage    = usage,
            model_id = "test/model"
        )

        assert breakdown.prompt_tokens == 800
        assert breakdown.prompt_cost == Safe_Float("0.00012")         # 800 * 0.15/1M
        assert breakdown.cache_read_cost == Safe_Float("0.000015")    # 200 * 0.075/1M
        assert breakdown.cache_write_cost == Safe_Float("0.00012")    # 800 * 0.15/1M

        total_expected = Safe_Float("0.00012") + Safe_Float("0.0003") + Safe_Float("0.000015") + Safe_Float("0.00012")
        assert breakdown.total_cost == total_expected

    def test__calculate_from_pricing__with_images(self):            # Test calculation with image processing
        usage = {
            "prompt_tokens"     : 1000,
            "completion_tokens" : 500,
            "total_tokens"      : 1500,
            "images"            : 3      # 3 images processed
        }

        breakdown = self.cost_service._calculate_from_pricing(
            pricing  = self.mock_pricing,
            usage    = usage,
            model_id = "test/model"
        )

        assert breakdown.image_cost == Safe_Float("0.03")  # 3 * 0.01
        assert breakdown.total_cost == Safe_Float("0.00045") + Safe_Float("0.03")

    def test__calculate_from_pricing__free_model(self):     # Test calculation for free models
        usage = {
            "prompt_tokens"     : 10000,
            "completion_tokens" : 5000,
            "total_tokens"      : 15000
        }

        breakdown = self.cost_service._calculate_from_pricing(
            pricing  = self.free_pricing,
            usage    = usage,
            model_id = "free/model"
        )

        assert breakdown.prompt_cost == Safe_Float("0")
        assert breakdown.completion_cost == Safe_Float("0")
        assert breakdown.total_cost == Safe_Float("0")
        assert breakdown.cost_per_1k_tokens == Safe_Float("0")

    def test__cost_breakdown_to_display_dict(self):
        """Test cost breakdown display formatting"""
        breakdown = Schema__Open_Router__Cost_Breakdown(prompt_tokens      = 1000,
                                                        completion_tokens  = 500,
                                                        total_tokens       = 1500,
                                                        prompt_cost        = Safe_Float("0.00015"   ),
                                                        completion_cost    = Safe_Float("0.0003"    ),
                                                        total_cost         = Safe_Float("0.00045"   ),
                                                        cost_per_1k_tokens = Safe_Float("0.0003"    ),
                                                        model_id           = "openai/gpt-4o-mini",
                                                        provider           = "openai"            )

        display = breakdown.to_display_dict()

        assert display == {
            "prompt_tokens"     : "1000",
            "completion_tokens" : "500",
            "total_tokens"      : "1500",
            "prompt_cost"       : "$0.000150",
            "completion_cost"   : "$0.000300",
            "total_cost"        : "$0.000450",
            "cost_per_1k"       : "$0.000300",
            "model"             : "openai/gpt-4o-mini",
            "provider"          : "openai"
        }

    @pytest.mark.skip("review test and check performance")
    @patch.object(Service__Open_Router__Cost, 'models_service')
    def test__bug__calculate_cost(self, mock_models_service):        # Test calculate_cost with model lookup
        # Mock model with pricing
        mock_model = Mock(spec=Schema__Open_Router__Model)
        mock_model.pricing = self.mock_pricing
        mock_models_service.get_model_by_id.return_value = mock_model

        usage = {   "prompt_tokens"     : 2000,
                    "completion_tokens" : 1000,
                    "total_tokens"      : 3000
        }

        breakdown = self.cost_service.calculate_cost(model_id = "openai/gpt-4o-mini",
                                                     usage    = usage,
                                                     provider = "openai")

        assert breakdown.prompt_tokens      == 2000
        assert breakdown.completion_tokens  == 1000
        assert breakdown.prompt_cost        != Safe_Float(0.0003)    # 2000 * 0.15/1M
        assert breakdown.prompt_cost        == Safe_Float(3e-10)     # BUG? is this the correct value

        assert breakdown.completion_cost    != Safe_Float(0.0006)    # 1000 * 0.60/1M
        assert breakdown.completion_cost    == Safe_Float(6e-10)    # BUG? is this the correct value

        assert breakdown.total_cost         != Safe_Float(0.0009)
        assert breakdown.total_cost         == Safe_Float(9e-10 )   # BUG? is this the correct value

    @patch.object(Service__Open_Router__Cost, 'models_service')
    def test__calculate_cost__no_pricing(self, mock_models_service):
        """Test error when model has no pricing"""