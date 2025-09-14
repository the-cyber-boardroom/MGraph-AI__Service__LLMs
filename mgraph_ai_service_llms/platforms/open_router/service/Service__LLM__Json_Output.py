from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.llm.safe_str.Safe_Str__LLM__Model_Id                          import Safe_Str__LLM__Model_Id
from osbot_utils.type_safe.primitives.domains.llm.safe_float.Safe_Float__LLM__Temperature                   import Safe_Float__LLM__Temperature
from osbot_utils.type_safe.primitives.domains.llm.safe_uint.Safe_UInt__LLM__Max_Tokens                      import Safe_UInt__LLM__Max_Tokens
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                              import type_safe
from osbot_utils.utils.Json                                                                                 import json_to_str, str_to_json
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Json_Extract__Response        import Schema__Json_Extract__Response
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Provider_Preferences import Schema__Open_Router__Provider_Preferences
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                              import Service__Open_Router
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Chat_Request         import Schema__Open_Router__Chat_Request
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Message              import Schema__Open_Router__Message
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Response_Format      import Schema__Open_Router__Response_Format
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Message_Content                 import Safe_Str__Message_Content
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_ID                   import Safe_Str__Open_Router__Model_ID
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers               import Schema__Open_Router__Providers

#T = TypeVar('T', bound=Type_Safe)

# Models that support native JSON mode (OpenAI standard)
JSON_MODE_MODELS = { "openai/gpt-4o"                                      ,
                     "openai/gpt-4o-mini"                                  ,
                     "openai/gpt-4.1-mini"                                 ,
                     "openai/gpt-5-nano"                                   ,
                     "openai/gpt-5-mini"                                   ,
                     "openai/gpt-oss-120b"                                 ,
                     "openai/gpt-oss-20b"                                  }


class Service__LLM__Json_Output(Type_Safe):                                                          # Service for generic JSON extraction
    open_router      : Service__Open_Router              = None
    default_model    : Safe_Str__LLM__Model_Id           = Safe_Str__LLM__Model_Id("openai/gpt-oss-20b")
    default_provider : Schema__Open_Router__Providers    = Schema__Open_Router__Providers.GROQ

    def __init__(self):
        super().__init__()
        self.open_router = Service__Open_Router()

    def extract(self, text_content   : Safe_Str__Message_Content                         ,           # Extract JSON using provided schema
                      output_schema  : dict                                              ,
                      model          : Safe_Str__LLM__Model_Id                   = None ,
                      provider       : Schema__Open_Router__Providers            = None ,
                      temperature    : Safe_Float__LLM__Temperature              = 0.0  ,
                      max_tokens     : Safe_UInt__LLM__Max_Tokens                = 5000
                ) -> Schema__Json_Extract__Response:

        provider             = provider or self.default_provider
        model_id             = model or self.default_model
        open_router_provider = self.resolve_open_router_provider(provider)

        system_prompt = f"""You are a JSON data extractor. Output ONLY valid JSON that matches this schema:

{json_to_str(output_schema, indent=2)}

Output ONLY the JSON object with no explanations, markdown, or comments."""

        user_prompt = f"Extract structured data from: {text_content}"

        messages = [ Schema__Open_Router__Message(role    = "system"                              ,  # Build messages
                                                   content = Safe_Str__Message_Content(system_prompt)),
                     Schema__Open_Router__Message(role    = "user"                                ,
                                                   content = Safe_Str__Message_Content(user_prompt))  ]

        chat_request = Schema__Open_Router__Chat_Request(model           = Safe_Str__Open_Router__Model_ID(str(model_id))          ,                     # Create request with JSON mode
                                                         messages        = messages                                                ,
                                                         temperature     = temperature                                             ,
                                                         max_tokens      = max_tokens                                              ,
                                                         response_format = Schema__Open_Router__Response_Format(type="json_object" ),                     # Use JSON mode
                                                         provider        = open_router_provider                                    )

        response      = self.open_router.chat_completion__execute_request(chat_request)
        response_text = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")     # Extract response
        cache_id      = response.get("cache_id", "")
        duration      = response.get("duration", None)
        provider      = provider
        json_data     = str_to_json(response_text)
        tokens        = response.get('usage', {}).get('total_tokens',0)

        return Schema__Json_Extract__Response(cache_id  = cache_id ,
                                              duration  = duration ,
                                              json_data = json_data,
                                              model     = model_id ,
                                              provider  = provider ,
                                              tokens    = tokens   )

    @type_safe
    def resolve_open_router_provider(self, provider: Schema__Open_Router__Providers=None):
        if provider:
            kwargs = dict(allow_fallbacks = False,
                          order           = [provider.value])
            return Schema__Open_Router__Provider_Preferences(**kwargs)
        return None


