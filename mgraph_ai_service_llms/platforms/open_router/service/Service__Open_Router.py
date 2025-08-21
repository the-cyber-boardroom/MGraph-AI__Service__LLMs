# mgraph_ai_service_llms/platforms/open_router/service/Service__Open_Router.py
import json
import requests
from typing                                                                                             import Dict, Any, Optional, Iterator

from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Env                                                                              import get_env

from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Chat__Cache import Open_Router__Chat__Cache
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_ID               import Safe_Str__Open_Router__Model_ID
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Chat_Request     import Schema__Open_Router__Chat_Request
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Provider_Preferences import Schema__Open_Router__Provider_Preferences
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Request_Headers  import Schema__Open_Router__Request_Headers
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Message_Content             import Safe_Str__Message_Content
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router__Models                  import Service__Open_Router__Models
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router__Cost                    import Service__Open_Router__Cost
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Message          import Schema__Open_Router__Message

ENV_NAME_OPEN_ROUTER__API_KEY = "OPEN_ROUTER__API_KEY"


class Service__Open_Router(Type_Safe):                                                                   # Main service for OpenRouter API interactions

    api_base_url   : str                        = "https://openrouter.ai/api"
    models_service : Service__Open_Router__Models = None
    cost_service   : Service__Open_Router__Cost   = None

    def __init__(self):
        super().__init__()
        self.models_service = Service__Open_Router__Models()
        self.cost_service   = Service__Open_Router__Cost()

    def api_key(self) -> str:                                                                            # Get API key from environment
        api_key = get_env(ENV_NAME_OPEN_ROUTER__API_KEY)
        if not api_key:
            raise ValueError(f"API key not found in environment variable: {ENV_NAME_OPEN_ROUTER__API_KEY}")
        return api_key

    @cache_on_self
    def chat_cache(self):
        return Open_Router__Chat__Cache().setup()

    def chat_completion_url(self) -> str:                                                                # Get chat completion endpoint URL
        return f"{self.api_base_url}/v1/chat/completions"

    def create_headers(self, max_cost      : Optional[float] = None ,                                    # Create request headers with optional parameters
                             provider       : Optional[str  ] = None ,
                             include_provider : bool          = True
                       ) -> Schema__Open_Router__Request_Headers:
        headers = Schema__Open_Router__Request_Headers.create_default(api_key = self.api_key())

        if max_cost is not None:
            headers.with_max_cost(max_cost)

        if provider:
            headers.with_provider(provider)

        headers.x_include_provider = include_provider

        return headers

    def chat_completion(self, prompt       : str                                        ,                # Execute standard chat completion request
                              model         : str                                        ,
                              system_prompt : Optional[str  ]                    = None ,
                              temperature   : float                               = 0.7  ,
                              max_tokens    : int                                = 5000 ,
                              provider      : Optional[str  ]                    = None ,
                              max_cost      : Optional[float]                    = None
                        ) -> Dict[str, Any]:
        kwargs = dict(model         = Safe_Str__Open_Router__Model_ID(model)      ,
                      prompt        = Safe_Str__Message_Content(prompt)           ,
                      system_prompt = Safe_Str__Message_Content(system_prompt) if system_prompt else None,
                      temperature   = temperature                                  ,
                      max_tokens    = max_tokens)
        if provider:
            kwargs['provider'] = Schema__Open_Router__Provider_Preferences(order=[provider], allow_fallbacks=False)

        request = Schema__Open_Router__Chat_Request.create_simple(**kwargs)

        request_data = request.json()
        cached_response = self.chat_cache().get_cached_response(request_data)
        if cached_response:
            cached_response['from_cache'] = True
            return cached_response


        headers = self.create_headers(max_cost        = max_cost ,
                                      provider        = provider ,
                                      include_provider = True    )

        response = requests.post(url     = self.chat_completion_url()     ,
                                 headers = headers.to_headers_dict()       ,
                                 json    = request.to_api_dict()           )
        if response.status_code == 400:
            pprint(response.json())
        response.raise_for_status()                                                                      # Raise exception for HTTP errors
        response_data = response.json()

        if "usage" in response_data:                                                                     # Calculate costs if usage data available
            try:
                cost_breakdown = self.cost_service.calculate_cost(
                    model_id = Safe_Str__Open_Router__Model_ID(model),
                    usage    = response_data["usage"]                 ,
                    provider = response_data.get("provider")
                )
                response_data["cost_breakdown"] = cost_breakdown.to_display_dict()
            except Exception:
                pass                                                                                      # Ignore cost calculation errors

        self.chat_cache().cache_chat_response(request_data, response_data)
        return response_data

    # todo :add cache support
    def chat_completion_stream(self, prompt       : str                         ,                        # Execute streaming chat completion request
                                     model         : str                         ,
                                     system_prompt : Optional[str  ]     = None ,
                                     temperature   : float                = 0.7  ,
                                     max_tokens    : int                  = 1000 ,
                                     provider      : Optional[str  ]     = None ,
                                     max_cost      : Optional[float]     = None
                               ) -> Iterator[Dict[str, Any]]:

        messages = []
        if system_prompt:
            messages.append(Schema__Open_Router__Message(role    = "system"                           ,
                                                         content = Safe_Str__Message_Content(system_prompt)))
        messages.append(Schema__Open_Router__Message(role    = "user"                                 ,
                                                     content = Safe_Str__Message_Content(prompt)      ))

        request = Schema__Open_Router__Chat_Request(
            model       = Safe_Str__Open_Router__Model_ID(model),
            messages    = messages                               ,
            temperature = temperature                            ,
            max_tokens  = max_tokens                             ,
            stream      = True                                                                           # Enable streaming
        )

        headers = self.create_headers(max_cost        = max_cost ,
                                      provider        = provider ,
                                      include_provider = True    )

        response = requests.post(url     = self.chat_completion_url()               ,                    # Use requests for streaming
                                headers = headers.to_headers_dict()                 ,
                                json    = request.to_api_dict()                     ,
                                stream  = True                                       )

        response.raise_for_status()                                                                      # Raise exception for HTTP errors

        for line in response.iter_lines():                                                               # Process Server-Sent Events
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]                                                              # Remove 'data: ' prefix

                    if data_str == '[DONE]':
                        break

                    try:
                        chunk_data = json.loads(data_str)
                        yield chunk_data
                    except json.JSONDecodeError:
                        continue                                                                          # Skip invalid JSON

    def list_models(self, include_free : bool = True ,                                                   # Get list of available models with optional filtering
                          include_paid : bool = True
                    ) -> Dict[str, Any]:
        models = self.models_service.api__models()

        filtered_models = []
        for model in models:
            is_free = (float(model.pricing.prompt) == 0 and float(model.pricing.completion) == 0)

            if (is_free and include_free) or (not is_free and include_paid):
                filtered_models.append({
                    "id"             : str(model.id)                       ,
                    "name"           : str(model.name)                     ,
                    "context_length" : model.context_length                ,
                    "is_free"        : is_free                             ,
                    "pricing"        : model.pricing.json() if model.pricing else None
                })

        return { "models" : filtered_models        ,
                 "total"  : len(filtered_models)   }

    def estimate_cost(self, model         : str ,                                                        # Estimate cost before making request
                            prompt_length  : int ,
                            max_tokens     : int
                      ) -> Dict[str, Any]:

        prompt_tokens = prompt_length // 4                                                               # Rough estimate: 1 token ≈ 4 chars

        cost_breakdown = self.cost_service.estimate_cost(
            model_id      = Safe_Str__Open_Router__Model_ID(model),
            prompt_tokens = prompt_tokens                          ,
            max_tokens    = max_tokens
        )

        return { "model"          : model                                  ,
                 "estimated_cost" : cost_breakdown.to_display_dict()       ,
                 "prompt_tokens"  : prompt_tokens                          ,
                 "max_tokens"     : max_tokens                             }

    def get_model_info(self, model_id : str                                                              # Get detailed information about a specific model
                       ) -> Optional[Dict[str, Any]]:
        model = self.models_service.get_model_by_id(Safe_Str__Open_Router__Model_ID(model_id))

        if not model:
            return None

        return { "id"                   : str(model.id)                    ,
                 "name"                 : str(model.name)                  ,
                 "description"          : str(model.description)           ,
                 "context_length"       : model.context_length             ,
                 "architecture"         : { "modality"          : str(model.architecture.modality)         ,
                                           "tokenizer"         : str(model.architecture.tokenizer)        ,
                                           "input_modalities"  : model.architecture.input_modalities      ,
                                           "output_modalities" : model.architecture.output_modalities     },
                 "pricing"              : model.pricing.json() if model.pricing else None                  ,
                 "supported_parameters" : [str(p) for p in model.supported_parameters]                     }