from unittest                                                                                          import TestCase
from osbot_utils.type_safe.Type_Safe                                                                   import Type_Safe
from osbot_utils.utils.Objects                                                                         import base_classes
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Request_Headers import Schema__Open_Router__Request_Headers


class test_Schema__Open_Router__Request_Headers(TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup test instance with required fields"""
        cls.headers = Schema__Open_Router__Request_Headers( authorization = "Bearer test-api-key-123" ,
                                                            http_referer  = "https://test.example.com",
                                                            x_title       = "Test Application"        )

    def test_setUpClass(self):
        """Verify class setup and inheritance"""
        with self.headers as _:
            assert type(_) is Schema__Open_Router__Request_Headers
            assert base_classes(_) == [Type_Safe, object]
            assert _.authorization == "Bearer test-api-key-123"
            assert _.http_referer  == "https://test.example.com"
            assert _.x_title       == "Test Application"

    def test__to_headers_dict__minimal(self):
        """Test conversion to headers dict with minimal required fields"""
        headers_dict = self.headers.to_headers_dict()

        assert headers_dict == { "Authorization"       : "Bearer test-api-key-123"  ,
                                 "HTTP-Referer"        : "https://test.example.com" ,
                                 "X-Title"             : "Test Application"         ,
                                 "X-Include-Provider"  : "true"                     }       # Default value

    def test__to_headers_dict__with_provider_control(self):
        """Test headers with provider control options"""
        self.headers.x_provider = "openai"
        self.headers.providers  = ["openai", "anthropic", "groq"]
        self.headers.x_include_provider = False

        headers_dict = self.headers.to_headers_dict()

        assert headers_dict["X-Provider"]        == "openai"
        assert headers_dict["providers"]         == "openai,anthropic,groq"
        assert headers_dict["X-Include-Provider"] == "false"

    def test__to_headers_dict__with_routing(self):
        """Test headers with routing preferences"""
        self.headers.order   = ["groq", "cerebras", "together"]
        self.headers.require = ["streaming", "function-calling"]

        headers_dict = self.headers.to_headers_dict()

        assert headers_dict["order"]   == "groq,cerebras,together"
        assert headers_dict["require"] == "streaming,function-calling"

    def test__to_headers_dict__with_cost_control(self):
        """Test headers with cost control"""
        self.headers.x_max_cost = 0.5  # 50 cents maximum

        headers_dict = self.headers.to_headers_dict()

        assert headers_dict["X-Max-Cost"] == "0.5"

    def test__to_headers_dict__with_request_tracking(self):
        """Test headers with request tracking"""
        self.headers.x_request_id = "req-12345-67890"

        headers_dict = self.headers.to_headers_dict()

        assert headers_dict["X-Request-ID"] == "req-12345-67890"

    def test__create_default(self):
        """Test factory method for default headers"""
        headers = Schema__Open_Router__Request_Headers.create_default(api_key = "test-key-456")

        assert headers.authorization == "Bearer test-key-456"
        assert headers.http_referer  == "https://github.com/the-cyber-boardroom/MGraph-AI__Service__LLMs"
        assert headers.x_title       == "MGraph-AI LLM Service"
        assert headers.x_include_provider == True

        # Test with custom values
        headers_custom = Schema__Open_Router__Request_Headers.create_default(
            api_key = "test-key-789"        ,
            referer = "https://custom.app"  ,
            title   = "Custom App"           ,
        )

        assert headers_custom.authorization == "Bearer test-key-789"
        assert headers_custom.http_referer  == "https://custom.app"
        assert headers_custom.x_title       == "Custom App"

    def test__fluent_methods(self):
        """Test fluent interface methods for building headers"""
        headers = (Schema__Open_Router__Request_Headers
                        .create_default     ("test-key")
                        .with_provider      ("anthropic")
                        .with_provider_order("anthropic", "openai", "groq")
                        .with_requirements  ("streaming", "json-mode")
                        .with_max_cost      (1.0))

        assert headers.x_provider == "anthropic"
        assert headers.order      == ["anthropic", "openai", "groq"]
        assert headers.require    == ["streaming", "json-mode"]
        assert headers.x_max_cost == 1.0

        # Verify in headers dict
        headers_dict = headers.to_headers_dict()
        assert headers_dict["X-Provider"] == "anthropic"
        assert headers_dict["order"]      == "anthropic,openai,groq"
        assert headers_dict["require"]    == "streaming,json-mode"
        assert headers_dict["X-Max-Cost"] == "1.0"

    def test__all_fields_populated(self):
        """Test with all possible fields populated"""
        headers = Schema__Open_Router__Request_Headers(
            authorization       = "Bearer full-test-key"          ,
            http_referer       = "https://full.test.com"         ,
            x_title            = "Full Test"                     ,
            x_provider         = "openai"                        ,
            providers          = ["openai", "anthropic"]         ,
            x_include_provider = True                            ,
            order              = ["anthropic", "openai"]         ,
            require            = ["streaming"]                   ,
            x_request_id       = "req-full-test"                 ,
            x_max_cost         = 2.5                             ,
        )

        headers_dict = headers.to_headers_dict()

        # Verify all headers present
        expected_keys = [
            "Authorization", "HTTP-Referer", "X-Title", "X-Provider",
            "providers", "X-Include-Provider", "order", "require",
            "X-Request-ID", "X-Max-Cost"
        ]

        assert sorted(headers_dict.keys()) == sorted(expected_keys)

        # Verify values
        assert headers_dict["Authorization"]       == "Bearer full-test-key"
        assert headers_dict["HTTP-Referer"]        == "https://full.test.com"
        assert headers_dict["X-Title"]             == "Full Test"
        assert headers_dict["X-Provider"]          == "openai"
        assert headers_dict["providers"]           == "openai,anthropic"
        assert headers_dict["X-Include-Provider"]  == "true"
        assert headers_dict["order"]               == "anthropic,openai"
        assert headers_dict["require"]             == "streaming"
        assert headers_dict["X-Request-ID"]        == "req-full-test"
        assert headers_dict["X-Max-Cost"]          == "2.5"