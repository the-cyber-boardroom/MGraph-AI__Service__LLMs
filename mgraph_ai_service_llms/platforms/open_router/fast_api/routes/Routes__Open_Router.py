import json
from typing                                                                                          import Dict, Any, Optional
from fastapi                                                                                         import HTTPException
from fastapi.responses                                                                               import StreamingResponse
from osbot_fast_api.api.routes.Fast_API__Routes                                                      import Fast_API__Routes
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Tag                                           import Safe_Str__Fast_API__Route__Tag
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                       import Service__Open_Router
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers        import Schema__Open_Router__Providers
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Supported_Models import Schema__Open_Router__Supported_Models


class Routes__Open_Router(Fast_API__Routes):
    tag           : Safe_Str__Fast_API__Route__Tag = 'chat'
    open_router   : Service__Open_Router           = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.open_router = Service__Open_Router()

    def complete(self, prompt       : str                                              ,                # Standard chat completion endpoint
                       model         : Schema__Open_Router__Supported_Models           ,
                       system_prompt : Optional[str  ]                          = None ,
                       temperature   : float                                    = 0.7  ,
                       max_tokens    : int                                      = 1000 ,
                       provider      : Optional[Schema__Open_Router__Providers] = None ,
                       max_cost      : Optional[float]                          = None
                 ) -> Dict[str, Any]:
        try:
            provider_str = provider.value if provider else None

            response = self.open_router.chat_completion(
                prompt        = prompt                ,
                model         = model.value            ,
                system_prompt = system_prompt          ,
                temperature   = temperature            ,
                max_tokens    = max_tokens             ,
                provider      = provider_str           ,
                max_cost      = max_cost
            )

            return { "status"   : "success"                                            ,
                     "model"    : model.value                                          ,
                     "provider" : response.get("provider", provider_str or "auto")     ,
                     "response" : response.get("choices", [{}])[0].get("message", {}).get("content", ""),
                     "usage"    : response.get("usage", {})                            ,
                     "cost"     : response.get("cost_breakdown", {})                   }

        except ValueError as e:
            raise HTTPException(status_code = 400          ,
                               detail      = str(e)        )
        except Exception as e:
            raise HTTPException(status_code = 500                       ,
                               detail      = f"Internal error: {str(e)}")

    def complete_stream(self, prompt       : str                                               ,         # Streaming chat completion endpoint
                              model         : Schema__Open_Router__Supported_Models           ,
                              system_prompt : Optional[str  ]                          = None ,
                              temperature   : float                                     = 0.7  ,
                              max_tokens    : int                                       = 1000 ,
                              provider      : Optional[Schema__Open_Router__Providers] = None ,
                              max_cost      : Optional[float]                          = None
                        ):

        def generate():                                                                                  # Generator function for streaming response
            try:
                provider_str = provider.value if provider else None

                for chunk in self.open_router.chat_completion_stream(
                    prompt        = prompt           ,
                    model         = model.value       ,
                    system_prompt = system_prompt     ,
                    temperature   = temperature       ,
                    max_tokens    = max_tokens        ,
                    provider      = provider_str      ,
                    max_cost      = max_cost
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"                                              # SSE format

                yield "data: [DONE]\n\n"                                                                # Signal end of stream

            except Exception as e:
                error_msg = { "error" : str(e)                 ,
                             "type"  : "stream_error"          }
                yield f"data: {json.dumps(error_msg)}\n\n"

        return StreamingResponse(generate()                    ,
                                media_type = "text/event-stream")

    def models(self, include_free : bool = True ,                                                       # List available models
                     include_paid : bool = True
               ) -> Dict[str, Any]:
        try:
            return self.open_router.list_models(include_free = include_free ,
                                               include_paid = include_paid )
        except Exception as e:
            raise HTTPException(status_code = 500                       ,
                               detail      = f"Failed to fetch models: {str(e)}")

    def model_info(self, model_id : str                                                                 # Get detailed model information
                   ) -> Dict[str, Any]:
        model_info = self.open_router.get_model_info(model_id)

        if not model_info:
            raise HTTPException(status_code = 404                               ,
                               detail      = f"Model not found: {model_id}"    )

        return model_info

    def estimate_cost(self, model         : Schema__Open_Router__Supported_Models ,                     # Estimate cost for a request
                            prompt_length  : int                                   ,
                            max_tokens     : int
                      ) -> Dict[str, Any]:
        try:
            return self.open_router.estimate_cost(model         = model.value    ,
                                                 prompt_length = prompt_length   ,
                                                 max_tokens    = max_tokens      )
        except ValueError as e:
            raise HTTPException(status_code = 400          ,
                               detail      = str(e)        )
        except Exception as e:
            raise HTTPException(status_code = 500                                      ,
                               detail      = f"Failed to estimate cost: {str(e)}"    )

    def providers(self) -> Dict[str, Any]:                                                              # List available providers
        return { "providers" : [ { "id"          : provider.value                      ,
                                   "name"        : provider.name                        ,
                                   "header_value": provider.header_value()              }
                                 for provider in Schema__Open_Router__Providers       ] }

    def setup_routes(self):
        self.add_route_post(self.complete         )
        self.add_route_post(self.complete_stream  )
        self.add_route_get (self.models           )
        self.add_route_get (self.model_info       )
        self.add_route_post(self.estimate_cost    )
        self.add_route_get (self.providers        )