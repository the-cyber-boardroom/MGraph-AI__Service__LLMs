from typing                                                                                          import Dict, Any, Optional
from osbot_utils.type_safe.Type_Safe                                                                 import Type_Safe
from osbot_utils.decorators.methods.cache_on_self                                                    import cache_on_self
from osbot_utils.type_safe.primitives.safe_float.Safe_Float                                          import Safe_Float
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_ID            import Safe_Str__Open_Router__Model_ID
from mgraph_ai_service_llms.platforms.open_router.Service__Open_Router__Models                       import Service__Open_Router__Models
from mgraph_ai_service_llms.platforms.open_router.schemas.cost.Schema__Open_Router__Cost_Breakdown   import Schema__Open_Router__Cost_Breakdown
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Pricing import Schema__Open_Router__Model__Pricing





class Service__Open_Router__Cost(Type_Safe):
    """Service for calculating and tracking OpenRouter API costs

    Provides cost calculation, estimation, and tracking functionality
    for OpenRouter API usage across different models and providers.
    """

    models_service : Service__Open_Router__Models = None

    def __init__(self):
        super().__init__()
        self.models_service = Service__Open_Router__Models()

    def calculate_cost(self, model_id : Safe_Str__Open_Router__Model_ID,
                             usage    : Dict[str, int],
                             provider : Optional[str] = None
                        ) -> Schema__Open_Router__Cost_Breakdown:      # Calculate cost based on usage and model pricing

        # Get model info for pricing
        model_info = self.models_service.get_model_by_id(model_id)

        if not model_info or not model_info.pricing:
            raise ValueError(f"No pricing information available for model: {model_id}")

        return self._calculate_from_pricing(pricing  = model_info.pricing,
                                            usage    = usage             ,
                                            model_id = model_id          ,
                                            provider = provider          )

    def _calculate_from_pricing(self, pricing  : Schema__Open_Router__Model__Pricing,
                                      usage    : Dict[str, int],
                                      model_id : Safe_Str__Open_Router__Model_ID,
                                      provider : Optional[str] = None
                              ) -> Schema__Open_Router__Cost_Breakdown:
        """Internal method to calculate costs from pricing data"""

        # Extract token counts
        prompt_tokens     = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens      = usage.get("total_tokens", prompt_tokens + completion_tokens)

        # Extract additional usage metrics
        cached_tokens     = usage.get("prompt_cache_hit_tokens", 0)
        cache_write_tokens = usage.get("prompt_cache_miss_tokens", 0)
        images_processed  = usage.get("images", 0)
        audio_seconds     = usage.get("audio_seconds", 0)
        web_searches      = usage.get("web_searches", 0)
        reasoning_tokens  = usage.get("reasoning_tokens", 0)

        # Calculate base costs (convert from per million to actual cost)
        prompt_cost     = self._calculate_token_cost(prompt_tokens, pricing.prompt)
        completion_cost = self._calculate_token_cost(completion_tokens, pricing.completion)

        # Calculate additional costs
        cache_read_cost  = None
        cache_write_cost = None
        image_cost       = None
        audio_cost       = None
        web_search_cost  = None
        reasoning_cost   = None
        request_cost     = None

        if cached_tokens > 0 and pricing.input_cache_read:
            cache_read_cost = self._calculate_token_cost(cached_tokens, pricing.input_cache_read)

        if cache_write_tokens > 0 and pricing.input_cache_write:
            cache_write_cost = self._calculate_token_cost(cache_write_tokens, pricing.input_cache_write)

        if images_processed > 0 and pricing.image:
            image_cost = Safe_Float(str(pricing.image)) * Safe_Float(images_processed)

        if audio_seconds > 0 and pricing.audio:
            audio_cost = Safe_Float(str(pricing.audio)) * Safe_Float(audio_seconds)

        if web_searches > 0 and pricing.web_search:
            web_search_cost = Safe_Float(str(pricing.web_search)) * Safe_Float(web_searches)

        if reasoning_tokens > 0 and pricing.internal_reasoning:
            reasoning_cost = self._calculate_token_cost(reasoning_tokens, pricing.internal_reasoning)

        if pricing.request:
            request_cost = Safe_Float(str(pricing.request))

        # Calculate total cost
        total_cost = prompt_cost + completion_cost

        for additional_cost in [cache_read_cost, cache_write_cost, image_cost,
                               audio_cost, web_search_cost, reasoning_cost, request_cost]:
            if additional_cost:
                total_cost += additional_cost

        # Calculate cost per 1k tokens
        if total_tokens > 0:
            cost_per_1k = (total_cost / Safe_Float(total_tokens)) * Safe_Float("1000")
        else:
            cost_per_1k = Safe_Float("0")

        return Schema__Open_Router__Cost_Breakdown(
            prompt_tokens      = prompt_tokens                           ,
            completion_tokens  = completion_tokens                       ,
            total_tokens       = total_tokens                            ,
            prompt_cost        = prompt_cost                             ,
            completion_cost    = completion_cost                         ,
            cache_read_cost    = cache_read_cost                         ,
            cache_write_cost   = cache_write_cost                        ,
            image_cost         = image_cost                              ,
            audio_cost         = audio_cost                              ,
            web_search_cost    = web_search_cost                         ,
            reasoning_cost     = reasoning_cost                          ,
            request_cost       = request_cost                            ,
            total_cost         = total_cost                              ,
            cost_per_1k_tokens = cost_per_1k                             ,
            model_id           = Safe_Str__Open_Router__Model_ID(model_id)                      ,
            provider           = provider                                 ,
        )

    def _calculate_token_cost(self, token_count : int,
                                    price_per_million : Any
                               ) -> Safe_Float:
        """Calculate cost for tokens given price per million

        Args:
            token_count: Number of tokens
            price_per_million: Price per million tokens

        Returns:
            Cost in USD as Safe_Float
        """
        if not price_per_million or token_count == 0:
            return Safe_Float("0")

        # Convert price to Safe_Float and calculate
        price = Safe_Float(str(price_per_million))
        tokens = Safe_Float(str(token_count))

        # Price is per million tokens
        cost = (tokens / Safe_Float("1000000")) * price

        return cost

    def estimate_cost(self,
                     model_id       : Safe_Str__Open_Router__Model_ID,
                     prompt_tokens  : int,
                     max_tokens     : int,
                     include_cache  : bool = False,
                     cache_hit_rate : float = 0.0
                    ) -> Schema__Open_Router__Cost_Breakdown:
        """Estimate cost before making a request

        Args:
            model_id: Model to use
            prompt_tokens: Estimated prompt tokens
            max_tokens: Maximum completion tokens
            include_cache: Whether to include cache estimates
            cache_hit_rate: Expected cache hit rate (0.0 to 1.0)

        Returns:
            Estimated cost breakdown
        """
        # Build estimated usage
        usage = {
            "prompt_tokens"     : prompt_tokens,
            "completion_tokens" : max_tokens,
            "total_tokens"      : prompt_tokens + max_tokens
        }

        if include_cache and cache_hit_rate > 0:
            cached_tokens = int(prompt_tokens * cache_hit_rate)
            usage["prompt_cache_hit_tokens"] = cached_tokens
            usage["prompt_tokens"] = prompt_tokens - cached_tokens

        return self.calculate_cost(model_id, usage)

    @cache_on_self
    def get_cheapest_models(self,
                           capability : Optional[str] = None,
                           limit      : int = 5
                          ) -> list[Dict[str, Any]]:
        """Get cheapest models, optionally filtered by capability

        Args:
            capability: Optional capability filter (e.g., "function-calling", "json-mode")
            limit: Number of models to return

        Returns:
            List of cheapest models with pricing info
        """
        models = self.models_service.api__models()

        # Filter by capability if specified
        if capability:
            models = [m for m in models if capability in m.supported_parameters]

        # Calculate cost per 1k tokens for sorting (average of prompt and completion)
        models_with_cost = []

        for model in models:
            if model.pricing and model.pricing.prompt and model.pricing.completion:
                prompt_price = float(model.pricing.prompt)
                completion_price = float(model.pricing.completion)

                # Skip models with -1 pricing (auto routing)
                if prompt_price < 0 or completion_price < 0:
                    continue

                # Average cost per 1k tokens
                avg_cost_per_1k = ((prompt_price + completion_price) / 2) / 1000

                models_with_cost.append({
                    "model_id"          : str(model.id)                    ,
                    "name"              : str(model.name)                  ,
                    "prompt_cost_per_m" : f"${prompt_price:.3f}"           ,
                    "completion_cost_per_m" : f"${completion_price:.3f}"   ,
                    "avg_cost_per_1k"   : f"${avg_cost_per_1k:.6f}"        ,
                    "context_length"    : model.context_length             ,
                    "is_free"           : prompt_price == 0 and completion_price == 0,
                })

        # Sort by average cost
        models_with_cost.sort(key=lambda x: float(x["avg_cost_per_1k"][1:]))  # Remove $ and convert

        return models_with_cost[:limit]

    def compare_model_costs(self,
                           model_ids      : list[Safe_Str__Open_Router__Model_ID],
                           prompt_tokens  : int,
                           completion_tokens : int
                          ) -> Dict[str, Schema__Open_Router__Cost_Breakdown]:
        """Compare costs across multiple models

        Args:
            model_ids: List of model IDs to compare
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Dictionary mapping model ID to cost breakdown
        """
        usage = {
            "prompt_tokens"     : prompt_tokens,
            "completion_tokens" : completion_tokens,
            "total_tokens"      : prompt_tokens + completion_tokens
        }

        comparisons = {}

        for model_id in model_ids:
            try:
                cost_breakdown = self.calculate_cost(model_id, usage)
                comparisons[str(model_id)] = cost_breakdown
            except ValueError as e:
                # Skip models without pricing info
                continue

        return comparisons