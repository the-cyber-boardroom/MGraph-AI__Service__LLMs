from unittest                                                                                               import TestCase
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_float.Safe_Float                                                 import Safe_Float
from osbot_utils.utils.Objects                                                                              import base_classes, __
from osbot_utils.utils.Lists                                                                                import list_set
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Chat_Request         import Schema__Open_Router__Chat_Request
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Message              import  Schema__Open_Router__Message
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Provider_Preferences import Schema__Open_Router__Provider_Preferences
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Response_Format      import Schema__Open_Router__Response_Format
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Tool                 import Schema__Open_Router__Tool
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Tool__Function       import Schema__Open_Router__Tool__Function


class test_Schema__Open_Router__Chat_Request(TestCase):


    def setUp(self):                                                                        # Setup test chat request
        self.messages = [Schema__Open_Router__Message(role    = "system"                      ,
                                                     content = "You are a helpful assistant"),
                        Schema__Open_Router__Message(role    = "user"                        ,
                                                     content = "Hello, how are you?"         )]

        self.chat_request = Schema__Open_Router__Chat_Request(model    = "openai/gpt-4o-mini",
                                                             messages = self.messages        )

    def test_setUpClass(self):              # Verify class setup and inheritance
        with self.chat_request as _:
            assert type(_) is Schema__Open_Router__Chat_Request
            assert base_classes(_)      == [Type_Safe, object]
            assert _.model              == "openai/gpt-4o-mini"
            assert len(_.messages)      == 2
            assert _.messages[0].role   == "system"
            assert _.messages[1].role   == "user"

    def test__message_schema(self):         # Test message schema structure
        message = Schema__Open_Router__Message(role    = "assistant",
                                               content = "I'm doing well, thank you!")

        assert message.role == "assistant"
        assert message.content == "I'm doing well, thank you!"
        assert message.name is None
        assert message.tool_call_id is None

        # Test tool message
        tool_message = Schema__Open_Router__Message(
            role         = "tool",
            content      = '{"result": "success"}',
            name         = "function_name",
            tool_call_id = "call_123"
        )

        assert tool_message.role == "tool"
        assert tool_message.name == "function_name"
        assert tool_message.tool_call_id == "call_123"

    def test__to_api_dict__minimal(self):       # Test conversion to API dict with minimal fields
        api_dict = self.chat_request.to_api_dict()

        assert list_set(api_dict)              ==['messages', 'model']
        assert api_dict["model" ]              == "openai/gpt-4o-mini"
        assert len(api_dict["messages"])       == 2
        assert api_dict["messages"][0]["role"] == "system"
        assert api_dict["messages"][1]["role"] == "user"

    def test__to_api_dict__with_parameters(self):       # Test with standard generation parameters
        self.chat_request.temperature        = 0.7
        self.chat_request.max_tokens         = 1000
        self.chat_request.top_p              = 0.9
        self.chat_request.frequency_penalty  = 0.5
        self.chat_request.presence_penalty   = 0.5
        self.chat_request.seed               = 42

        api_dict = self.chat_request.to_api_dict()

        assert api_dict["temperature"      ] == 0.7
        assert api_dict["max_tokens"       ] == 1000
        assert api_dict["top_p"            ] == 0.9
        assert api_dict["frequency_penalty"] == 0.5
        assert api_dict["presence_penalty" ] == 0.5
        assert api_dict["seed"             ] == 42

    def test__response_format(self):                    # Test response format configuration
        # Default text format
        text_format = Schema__Open_Router__Response_Format()
        assert text_format.type == "text"

        # JSON format
        json_format = Schema__Open_Router__Response_Format(type="json_object")
        assert json_format.type == "json_object"

        # Apply to request
        self.chat_request.response_format = json_format
        api_dict = self.chat_request.to_api_dict()

        assert api_dict["response_format"]["type"] == "json_object"

    def test__tools_configuration(self):        # Test tools/functions configuration
        # Create a tool
        function = Schema__Open_Router__Tool__Function(
            name        = "get_weather",
            description = "Get weather for a location",
            parameters  = {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        )

        tool = Schema__Open_Router__Tool(type     = "function", function = function)

        # Add to request
        self.chat_request.tools = [tool]
        self.chat_request.tool_choice = "auto"

        api_dict = self.chat_request.to_api_dict()

        assert "tools" in api_dict
        assert len(api_dict["tools"]) == 1
        assert api_dict["tools"][0]["type"] == "function"
        assert api_dict["tools"][0]["function"]["name"] == "get_weather"
        assert api_dict["tool_choice"] == "auto"

    def test__provider_preferences(self):                        # Test provider preferences configuration
        preferences = Schema__Open_Router__Provider_Preferences(allow_fallbacks  = True                          ,
                                                                order            = ["anthropic", "openai", "groq"],
                                                                ignore_providers = ["together"                   ],
                                                                data_collection  = "deny"                        )

        self.chat_request.provider = preferences
        api_dict = self.chat_request.to_api_dict()

        assert "provider" in api_dict
        provider_dict = api_dict["provider"]
        assert provider_dict["allow_fallbacks"  ] == True
        assert provider_dict["order"            ] == ["anthropic", "openai", "groq"]
        assert provider_dict["ignore_providers" ] == ["together"]
        assert provider_dict["data_collection"  ] == "deny"

    def test__streaming_configuration(self):                    # Test streaming configuration
        assert self.chat_request.stream == False  # Default

        self.chat_request.stream = True
        api_dict = self.chat_request.to_api_dict()

        assert api_dict["stream"] == True

    def test__advanced_features(self):          # Test advanced features configuration
        self.chat_request.transforms = ["middle-out"]
        self.chat_request.models     = ["openai/gpt-4", "anthropic/claude-3"]
        self.chat_request.route      = "fallback"
        self.chat_request.stop       = ["END", "STOP"]

        api_dict = self.chat_request.to_api_dict()

        assert api_dict["transforms"] == ["middle-out"]
        assert api_dict["models"    ] == ["openai/gpt-4", "anthropic/claude-3"]
        assert api_dict["route"     ] == "fallback"
        assert api_dict["stop"      ] == ["END", "STOP"]

    def test__sampling_parameters(self):        # Test additional sampling parameters
        self.chat_request.min_p        = 0.1
        self.chat_request.top_a        = 0.5
        self.chat_request.top_k        = 40
        self.chat_request.logprobs     = True
        self.chat_request.top_logprobs = 5
        self.chat_request.logit_bias   = {"123": 0.5, "456": -0.5}

        api_dict = self.chat_request.to_api_dict()

        assert api_dict["min_p"] == 0.1
        assert api_dict["top_a"] == 0.5
        assert api_dict["top_k"] == 40
        assert api_dict["logprobs"] == True
        assert api_dict["top_logprobs"] == 5
        assert api_dict["logit_bias"] == {"123": 0.5, "456": -0.5}

    def test__create_simple(self):  # Test factory method for simple requests"""
        request = Schema__Open_Router__Chat_Request.create_simple(model  = "openai/gpt-4o-mini"            , # Without system prompt
                                                                  prompt = "What is the capital of France?")

        assert request.model == "openai/gpt-4o-mini"
        assert len(request.messages) == 1
        assert request.messages[0].role == "user"
        assert request.messages[0].content == "What is the capital of France?"


        # With system prompt
        request_with_system = Schema__Open_Router__Chat_Request.create_simple(model         = "openai/gpt-4o-mini"              ,
                                                                              prompt        = "What is the capital of France?"  ,
                                                                              system_prompt = "You are a geography expert"      ,
                                                                              temperature   = 0.5                               ,
                                                                              max_tokens    = 100                               )

        assert request_with_system.obj() == __(temperature       = 0.5                                 ,
                                               max_tokens        = 100                                 ,
                                               top_p             = None                                ,
                                               top_k             = None                                ,
                                               frequency_penalty = None                                ,
                                               presence_penalty  = None                                ,
                                               repetition_penalty= None                                ,
                                               seed              = None                                ,
                                               response_format   = None                                ,
                                               stop              = None                                ,
                                               tools             = None                                ,
                                               tool_choice       = None                                ,
                                               stream            = False                               ,
                                               provider          = None                                ,
                                               transforms        = None                                ,
                                               models            = None                                ,
                                               route             = None                                ,
                                               min_p             = None                                ,
                                               top_a             = None                                ,
                                               logit_bias        = None                                ,
                                               logprobs          = None                                ,
                                               top_logprobs      = None                                ,
                                               model             = 'openai/gpt-4o-mini'                ,
                                               messages          = [__(name         = None             ,
                                                                       tool_call_id = None             ,
                                                                       role         = 'system'         ,
                                                                       content      = 'You are a geography expert'),
                                                                    __(name         = None             ,
                                                                       tool_call_id = None             ,
                                                                       role         = 'user'           ,
                                                                       content      = 'What is the capital of France?')])




    def test__fluent_methods(self):         # Test fluent interface methods
        request = (Schema__Open_Router__Chat_Request
                   .create_simple("openai/gpt-4o-mini", "Test prompt")
                   .with_json_response()
                   .with_streaming()
                   .with_provider_preferences(
                       order=["openai", "anthropic"],
                       ignore=["together"],
                       allow_fallbacks=False
                   ))

        assert request.response_format.type == "json_object"
        assert request.stream == True
        assert request.provider.order == ["openai", "anthropic"]
        assert request.provider.ignore_providers == ["together"]
        assert request.provider.allow_fallbacks == False

        # Test with tools
        function = Schema__Open_Router__Tool__Function(
            name        = "test_function",
            description = "A test function",
            parameters  = {"type": "object"}
        )
        tool = Schema__Open_Router__Tool(type="function", function=function)

        request.with_tools([tool])

        assert len(request.tools) == 1
        assert request.tool_choice == "auto"

    def test__complete_request(self):           # Test a complete request with all features
        # Build comprehensive request
        request = Schema__Open_Router__Chat_Request(
            model              = "openai/gpt-4",
            messages           = self.messages,
            temperature        = 0.8,
            max_tokens         = 2000,
            top_p              = 0.95,
            top_k              = 50,
            frequency_penalty  = 0.3,
            presence_penalty   = 0.3,
            repetition_penalty = 1.1,
            seed               = 12345,
            response_format    = Schema__Open_Router__Response_Format(type="json_object"),
            stop               = ["END"],
            stream             = True,
            min_p              = 0.05,
            top_a              = 0.8,
            logprobs           = True,
            top_logprobs       = 3
        )

        assert request.to_api_dict() ==  {  'frequency_penalty' : 0.3                                             ,
                                            'logprobs'          : True                                            ,
                                            'max_tokens'        : 2000                                            ,
                                            'messages'          : [{'content'      : 'You are a helpful assistant',
                                                                    'name'         : None                         ,
                                                                    'role'         : 'system'                     ,
                                                                    'tool_call_id' : None}                        ,
                                                                   {'content'      : 'Hello, how are you?'        ,
                                                                    'name'         : None                         ,
                                                                    'role'         : 'user'                       ,
                                                                    'tool_call_id' : None}]                       ,
                                            'min_p'             : Safe_Float(0.05)                                ,
                                            'model'             : 'openai/gpt-4'                                  ,
                                            'presence_penalty'  : 0.3                                             ,
                                            'repetition_penalty': 1.1                                             ,
                                            'response_format'   : {'type': 'json_object'}                         ,
                                            'seed'              : 12345                                           ,
                                            'stop'              : ['END']                                         ,
                                            'stream'            : True                                            ,
                                            'temperature'       : 0.8                                             ,
                                            'top_a'             : Safe_Float(0.8)                                 ,
                                            'top_k'             : 50                                              ,
                                            'top_logprobs'      : 3                                               ,
                                            'top_p'             : 0.95                                            }
