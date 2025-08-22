from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__App_Title    import Safe_Str__App_Title
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Bearer_Token import Safe_Str__Bearer_Token
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Feature_Id   import Safe_Str__Feature_Id
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Provider_Id  import Safe_Str__Provider_Id
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Request_Id   import Safe_Str__Request_Id
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Requirement  import Safe_Str__Requirement

""" Complete OpenRouter request headers configuration

    Implements all available OpenRouter API headers for request control,
    provider routing, and response formatting.
"""

from typing                                                         import Optional, List, Dict
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.Safe_Str             import Safe_Str
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url    import Safe_Str__Url


class Schema__Open_Router__Request_Headers(Type_Safe):
    # Required headers
    authorization   : Safe_Str__Bearer_Token    # Bearer token
    http_referer    : Safe_Str__Url             # Your app URL
    x_title         : Safe_Str__App_Title       # App title for OpenRouter stats

    # Provider control headers
    x_provider      : Optional[Safe_Str__Provider_Id      ] = None  # Force specific provider (e.g., "openai", "anthropic")
    providers       : Optional[List[Safe_Str__Provider_Id]] = None  # Provider preferences/requirements

    # Response control
    x_include_provider: bool = True  # Include provider info in response

    # Advanced routing
    order             : Optional[List[Safe_Str__Provider_Id]] = None  # Provider preference order
    require           : Optional[List[Safe_Str__Feature_Id ]] = None  # Required provider features

    # Request tracking
    x_request_id: Optional[Safe_Str__Request_Id  ] = None  # Custom request ID for tracking

    # Cost control
    x_max_cost: Optional[float] = None  # Maximum cost allowed for request (in USD)

    # todo: refactor methods below into an Open_Router__Request_Headers

    def to_headers_dict(self) -> Dict[str, str]:
        """Convert to HTTP headers dictionary for API requests

        Returns properly formatted headers dict ready for HTTP requests.
        Only includes headers that have values set.
        """
        headers = {
            "Authorization": str(self.authorization),
            "HTTP-Referer": str(self.http_referer),
            "X-Title": str(self.x_title),
        }

        # Add optional provider control
        if self.x_provider:
            headers["X-Provider"] = str(self.x_provider)

        # Add provider preferences (comma-separated)
        if self.providers:
            headers["providers"] = ",".join(str(p) for p in self.providers)

        # Include provider info flag
        if self.x_include_provider:
            headers["X-Include-Provider"] = "true"
        else:
            headers["X-Include-Provider"] = "false"

        # Add routing preferences
        if self.order:
            headers["order"] = ",".join(str(o) for o in self.order)

        if self.require:
            headers["require"] = ",".join(str(r) for r in self.require)

        # Add request tracking
        if self.x_request_id:
            headers["X-Request-ID"] = str(self.x_request_id)

        # Add cost control
        if self.x_max_cost is not None:
            headers["X-Max-Cost"] = str(self.x_max_cost)

        return headers

    @classmethod
    def create_default(cls, api_key: str, referer: str = None, title: str = None):
        """Factory method to create headers with defaults

        Args:
            api_key: OpenRouter API key
            referer: Your application URL (defaults to GitHub repo)
            title: Your application title (defaults to MGraph-AI Service)
        """
        return cls( authorization = Safe_Str__Bearer_Token(f"Bearer {api_key}"),
                    http_referer  = Safe_Str__Url         (referer or "https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs"),
                    x_title       = Safe_Str__App_Title   (title or "MGraph-AI LLM Service")
        )

    def with_provider(self, provider: str):
        """Fluent method to set specific provider

        Args:
            provider: Provider name (e.g., "openai", "anthropic", "groq")

        Returns:
            Self for method chaining
        """
        self.x_provider = Safe_Str__Provider_Id(provider)
        return self

    def with_provider_order(self, *providers):
        """Fluent method to set provider preference order

        Args:
            *providers: Variable list of provider names in preference order

        Returns:
            Self for method chaining
        """
        self.order = [Safe_Str(p) for p in providers]
        return self

    def with_requirements(self, *requirements):
        """Fluent method to set required provider features

        Args:
            *requirements: Variable list of required features

        Returns:
            Self for method chaining
        """
        self.require = [Safe_Str__Requirement(r) for r in requirements]
        return self

    def with_max_cost(self, max_cost_usd: float):
        """Fluent method to set maximum cost limit

        Args:
            max_cost_usd: Maximum cost in USD

        Returns:
            Self for method chaining
        """
        self.x_max_cost = max_cost_usd
        return self