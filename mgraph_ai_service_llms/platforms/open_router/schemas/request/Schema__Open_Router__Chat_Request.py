# mgraph_ai_service_llms/platforms/open_router/schemas/Schema__Open_Router__Chat_Request.py

from typing                                                                                                 import Optional, List, Dict, Any, Literal
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_float.Safe_Float                                                 import Safe_Float
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                                     import Safe_Str
from osbot_utils.type_safe.primitives.safe_int.Safe_Int                                                     import Safe_Int
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_Name                 import Safe_Str__Open_Router__Model_Name
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Message_Content import Safe_Str__Message_Content
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Message              import Schema__Open_Router__Message
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Provider_Preferences import Schema__Open_Router__Provider_Preferences
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Response_Format      import Schema__Open_Router__Response_Format
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Tool                 import Schema__Open_Router__Tool

"""Complete OpenRouter chat completion request with all parameters

Implements the full OpenRouter API specification for chat completions
including streaming, tools, response formats, and provider routing.
"""

# todo: move the methods below to an Open_Router__Chat_Request class
class Schema__Open_Router__Chat_Request(Type_Safe):

    # Required fields
    model         : Safe_Str__Open_Router__Model_Name   # Model identifier
    messages      : List[Schema__Open_Router__Message]  # Conversation messages

    # Standard parameters
    temperature        : Optional[Safe_Float] = None  # 0.0 to 2.0                    # todo: use more specific version of Safe_Float
    max_tokens         : Optional[Safe_Int  ] = None  # Maximum tokens to generate
    top_p              : Optional[Safe_Float] = None     # Nucleus sampling
    top_k              : Optional[Safe_Int  ] = None  # Top-k sampling
    frequency_penalty  : Optional[Safe_Float] = None     # -2.0 to 2.0
    presence_penalty   : Optional[Safe_Float] = None     # -2.0 to 2.0
    repetition_penalty : Optional[Safe_Float] = None     # 0.0 to 2.0
    seed               : Optional[Safe_Int  ] = None  # For deterministic sampling

    # Response control
    response_format    : Optional[Schema__Open_Router__Response_Format] = None
    stop               : Optional[List[Safe_Str]] = None  # Stop sequences

    # Tools/Functions
    tools              : Optional[List[Schema__Open_Router__Tool]] = None
    tool_choice        : Optional[Safe_Str] = None  # "auto", "none", or specific tool

    # Streaming
    stream             : bool = False                # Enable SSE streaming

    # Provider routing
    provider           : Optional[Schema__Open_Router__Provider_Preferences] = None

    # Advanced features
    transforms         : List[Literal["middle-out"]                 ] = None  # ["middle-out"]
    models             : List[Safe_Str__Open_Router__Model_Name     ] = None  # Fallback models
    route              : Literal["fallback"                         ] = None  # Routing strategy

    # System prompts and context
    min_p              : Safe_Float            = None     # Min-p sampling
    top_a              : Safe_Float            = None     # Top-a sampling
    logit_bias         : Dict[str, Safe_Float] = None  # Token biases
    logprobs           : bool                  = None      # Return log probabilities
    top_logprobs       : Safe_Int              = None  # Number of logprobs

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary

        Returns dict formatted for OpenRouter API request.
        Only includes non-None values.
        """
        request_dict = {
            "model"    : str(self.model),
            "messages" : [msg.json() for msg in self.messages]
        }

        # Add optional parameters
        if self.temperature is not None:
            request_dict["temperature"] = self.temperature

        if self.max_tokens:
            request_dict["max_tokens"] = int(self.max_tokens)

        if self.top_p is not None:
            request_dict["top_p"] = self.top_p

        if self.top_k:
            request_dict["top_k"] = int(self.top_k)

        if self.frequency_penalty is not None:
            request_dict["frequency_penalty"] = self.frequency_penalty

        if self.presence_penalty is not None:
            request_dict["presence_penalty"] = self.presence_penalty

        if self.repetition_penalty is not None:
            request_dict["repetition_penalty"] = self.repetition_penalty

        if self.seed:
            request_dict["seed"] = int(self.seed)

        # Response format
        if self.response_format:
            request_dict["response_format"] = self.response_format.json()

        if self.stop:
            request_dict["stop"] = [str(s) for s in self.stop]

        # Tools
        if self.tools:
            request_dict["tools"] = [tool.json() for tool in self.tools]

        if self.tool_choice:
            request_dict["tool_choice"] = str(self.tool_choice)

        # Streaming
        if self.stream:
            request_dict["stream"] = True

        # Provider preferences
        if self.provider:
            request_dict["provider"] = self.provider.json()

        # Advanced features
        if self.transforms:
            request_dict["transforms"] = [str(t) for t in self.transforms]

        if self.models:
            request_dict["models"] = [str(m) for m in self.models]

        if self.route:
            request_dict["route"] = self.route

        # Additional sampling parameters
        if self.min_p is not None:
            request_dict["min_p"] = self.min_p

        if self.top_a is not None:
            request_dict["top_a"] = self.top_a

        if self.logit_bias:
            request_dict["logit_bias"] = self.logit_bias

        if self.logprobs is not None:
            request_dict["logprobs"] = self.logprobs

        if self.top_logprobs:
            request_dict["top_logprobs"] = int(self.top_logprobs)

        return request_dict

    @classmethod
    def create_simple(cls, model        : Safe_Str__Open_Router__Model_Name,
                           prompt       : Safe_Str__Message_Content,
                           system_prompt: Optional[Safe_Str__Message_Content] = None,
                           **kwargs):
        """Factory method for simple chat request

        Args:
            model: Model identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
        """
        messages = []

        if system_prompt:
            messages.append(Schema__Open_Router__Message(role    = "system",
                                                         content = system_prompt))

        messages.append(Schema__Open_Router__Message(role    = "user",
                                                     content = prompt))

        return cls(model    = model,
                   messages = messages,
                   **kwargs
        )

    def with_json_response(self):
        """Configure for JSON response format"""
        self.response_format = Schema__Open_Router__Response_Format(type="json_object")
        return self

    def with_streaming(self):
        """Enable streaming responses"""
        self.stream = True
        return self

    def with_tools(self, tools: List[Schema__Open_Router__Tool]):
        """Add tools/functions"""
        self.tools = tools
        self.tool_choice = Safe_Str("auto")
        return self

    def with_provider_preferences(self,
                                 order: Optional[List[str]] = None,
                                 ignore: Optional[List[str]] = None,
                                 allow_fallbacks: bool = True):
        """Configure provider preferences"""
        self.provider = Schema__Open_Router__Provider_Preferences(
            order           = [Safe_Str(p) for p in order] if order else None,
            ignore_providers = [Safe_Str(p) for p in ignore] if ignore else None,
            allow_fallbacks = allow_fallbacks
        )
        return self