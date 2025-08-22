from datetime                                                                          import datetime, timedelta
from unittest                                                                          import TestCase

from osbot_utils.type_safe.primitives.safe_str.cryptography.hashes.Safe_Str__Hash import Safe_Str__Hash

from memory_fs.file_fs.File_FS                                                        import File_FS
from memory_fs.file_types.Memory_FS__File__Type__Json                                 import Memory_FS__File__Type__Json
from osbot_aws.testing.Temp__Random__AWS_Credentials                                  import OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID, OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION
from osbot_aws.utils.AWS_Sanitization                                                 import str_to_valid_s3_bucket_name
from osbot_utils.type_safe.Type_Safe                                                  import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                    import Safe_Id
from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now                          import Timestamp_Now
from osbot_utils.utils.Misc                                                           import random_string_short
from osbot_utils.utils.Objects                                                        import base_classes
from osbot_aws.AWS_Config                                                             import aws_config
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache            import Open_Router__Cache
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Chat__Cache      import Open_Router__Chat__Cache
from tests.unit.Service__Fast_API__Test_Objs                                          import setup__service_fast_api_test_objs


class test_Open_Router__Chat__Cache(TestCase):                                        # Test chat cache implementation

    @classmethod
    def setUpClass(cls):                                                              # Initialize LocalStack and test cache
        cls.test_objs = setup__service_fast_api_test_objs()

        cls.test_bucket = str_to_valid_s3_bucket_name(random_string_short("test-chat-cache-"))
        cls.test_prefix = "chat"

        assert aws_config.account_id () == OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID
        assert aws_config.region_name() == OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION

        # Test request data
        cls.test_request_simple = {
            'model'       : 'openai/gpt-4o-mini'                             ,
            'messages'    : [{'role': 'user', 'content': 'Hello, world!'}]   ,
            'temperature' : 0.7                                              ,
            'max_tokens'  : 100
        }

        cls.test_request_with_system = {
            'model'       : 'openai/gpt-4o-mini'                                             ,
            'messages'    : [ {'role': 'system', 'content': 'You are a helpful assistant'}   ,
                             {'role': 'user'  , 'content': 'What is Python?'}              ],
            'temperature' : 0.5                                                              ,
            'max_tokens'  : 500                                                              ,
            'provider'    : 'openai'
        }

        cls.test_response_simple = {
            'choices'  : [{'message': {'content': 'Hello! How can I help you today?'}}],
            'usage'    : {'prompt_tokens': 10, 'completion_tokens': 15, 'total_tokens': 25},
            'model'    : 'openai/gpt-4o-mini'                                              ,
            'provider' : 'openai'
        }

        cls.test_response_complex = {
            'choices'  : [{'message': {'content': 'Python is a high-level programming language...'}}],
            'usage'    : {'prompt_tokens': 25, 'completion_tokens': 100, 'total_tokens': 125}       ,
            'model'    : 'openai/gpt-4o-mini'                                                       ,
            'provider' : 'openai'                                                                   ,
            'cost_breakdown': {'total_cost': 0.0001}
        }

        with Open_Router__Chat__Cache() as _:
            _.cache            = Open_Router__Cache(s3__bucket = cls.test_bucket,
                                                    s3__prefix = cls.test_prefix).setup()
            cls.chat_cache     = _
            _.setup()

    @classmethod
    def tearDownClass(cls):                                                           # Clean up test resources
        with cls.chat_cache.cache.s3__storage.s3 as _:
            if _.bucket_exists(cls.test_bucket):
                _.bucket_delete_all_files(cls.test_bucket)
                _.bucket_delete          (cls.test_bucket)

    def tearDown(self):                                                               # Clean up after each test
        self.chat_cache.cache.clear_all()

    def test__setUpClass(self):
        with self.chat_cache as _:
            assert type(_) is Open_Router__Chat__Cache

    def test__init__(self):                                                           # Test initialization
        cache = Open_Router__Chat__Cache()

        assert type(cache)           is Open_Router__Chat__Cache
        assert base_classes(cache)   == [Type_Safe, object]
        assert cache.cache           is None
        assert cache.cache_ttl_hours == 24

    def test_setup(self):                                                             # Test setup process
        cache = Open_Router__Chat__Cache()
        result = cache.setup()

        assert result                      is cache
        assert type(cache.cache)           is Open_Router__Cache
        assert cache.cache.s3__storage     is not None
        assert cache.cache.s3__prefix      == "chat"

    def test_generate_cache_id(self):                                                 # Test cache ID generation
        cache_id = self.chat_cache.generate_cache_id(self.test_request_simple)

        assert type(cache_id)    is Safe_Str__Hash
        assert len(str(cache_id)) == 10

        # Same request should generate same ID
        cache_id_2 = self.chat_cache.generate_cache_id(self.test_request_simple)
        assert cache_id == cache_id_2

        # Different request should generate different ID
        different_request = self.test_request_simple.copy()
        different_request['temperature'] = 0.9
        cache_id_3 = self.chat_cache.generate_cache_id(different_request)
        assert cache_id != cache_id_3

    def test_cache_chat_response(self):                                               # Test caching chat response
        result = self.chat_cache.cache_chat_response(self.test_request_simple,
                                                     self.test_response_simple)

        assert result is True

        # Verify cache entry structure
        cache_id = self.chat_cache.generate_cache_id(self.test_request_simple)
        file_id  = Safe_Id(cache_id)
        with self.chat_cache.cache.fs__latest_temporal.file__json(file_id) as _:
            assert _.exists()                       is True
            cached_data = _.content()
            assert cached_data['request' ]          == self.test_request_simple
            assert cached_data['response']          == self.test_response_simple
            assert 'cached_at' in cached_data
            assert cached_data['ttl_hours']         == 24

    def test_get_cached_response(self):                                               # Test retrieving cached response
        # Cache a response first
        self.chat_cache.cache_chat_response(self.test_request_simple,
                                           self.test_response_simple)

        # Retrieve it
        cached_response = self.chat_cache.get_cached_response(self.test_request_simple)

        assert cached_response == self.test_response_simple

    def test_get_cached_response_not_exists(self):                                    # Test retrieving non-existent cache
        cached_response = self.chat_cache.get_cached_response(self.test_request_simple)

        assert cached_response is None

    def test_get_cached_response_expired(self):                                       # Test expired cache handling
        # Cache a response
        cache_id = self.chat_cache.generate_cache_id(self.test_request_simple)
        file_id  = Safe_Id(cache_id)
        # Create cache entry with old timestamp
        old_timestamp = Timestamp_Now() - (25 * 3600 * 1000)                                 # 25 hours ago
        cache_entry = {
            'request'    : self.test_request_simple ,
            'response'   : self.test_response_simple,
            'cached_at'  : old_timestamp           ,
            'ttl_hours'  : 24
        }

        with self.chat_cache.cache.fs__latest_temporal.file__json(file_id) as _:
            _.create(cache_entry)

        # Should return None for expired cache
        cached_response = self.chat_cache.get_cached_response(self.test_request_simple)
        assert cached_response is None

    def test_cache_with_system_prompt(self):                                          # Test caching with system prompt
        result = self.chat_cache.cache_chat_response(self.test_request_with_system,
                                                     self.test_response_complex)

        assert result is True

        # Verify retrieval
        cached_response = self.chat_cache.get_cached_response(self.test_request_with_system)
        assert cached_response == self.test_response_complex

    def test_cache_different_models(self):                                            # Test caching for different models
        # Create requests for different models
        request_gpt4 = self.test_request_simple.copy()
        request_gpt4['model'] = 'openai/gpt-4'

        request_claude = self.test_request_simple.copy()
        request_claude['model'] = 'anthropic/claude-3'

        response_gpt4 = self.test_response_simple.copy()
        response_gpt4['model'] = 'openai/gpt-4'

        response_claude = self.test_response_simple.copy()
        response_claude['model'] = 'anthropic/claude-3'

        # Cache both
        self.chat_cache.cache_chat_response(request_gpt4  , response_gpt4  )
        self.chat_cache.cache_chat_response(request_claude, response_claude)

        # Each should have different cache ID
        cache_id_gpt4   = self.chat_cache.generate_cache_id(request_gpt4  )
        cache_id_claude = self.chat_cache.generate_cache_id(request_claude)
        assert cache_id_gpt4 != cache_id_claude

        # Each should retrieve correct response
        assert self.chat_cache.get_cached_response(request_gpt4  ) == response_gpt4
        assert self.chat_cache.get_cached_response(request_claude) == response_claude

    def test_cache_with_provider(self):                                               # Test provider-specific caching
        request_auto = self.test_request_simple.copy()
        request_auto['provider'] = 'auto'

        request_groq = self.test_request_simple.copy()
        request_groq['provider'] = 'groq'

        # Different providers should generate different cache IDs
        cache_id_auto = self.chat_cache.generate_cache_id(request_auto)
        cache_id_groq = self.chat_cache.generate_cache_id(request_groq)
        assert cache_id_auto != cache_id_groq

    def test_cache_temperature_sensitivity(self):                                     # Test temperature affects cache
        request_temp_05 = self.test_request_simple.copy()
        request_temp_05['temperature'] = 0.5

        request_temp_10 = self.test_request_simple.copy()
        request_temp_10['temperature'] = 1.0

        # Different temperatures should generate different cache IDs
        cache_id_05 = self.chat_cache.generate_cache_id(request_temp_05)
        cache_id_10 = self.chat_cache.generate_cache_id(request_temp_10)
        assert cache_id_05 != cache_id_10

    def test_cache_max_tokens_sensitivity(self):                                      # Test max_tokens affects cache
        request_100 = self.test_request_simple.copy()
        request_100['max_tokens'] = 100

        request_500 = self.test_request_simple.copy()
        request_500['max_tokens'] = 500

        # Different max_tokens should generate different cache IDs
        cache_id_100 = self.chat_cache.generate_cache_id(request_100)
        cache_id_500 = self.chat_cache.generate_cache_id(request_500)
        assert cache_id_100 != cache_id_500

    def test_cache_ttl_configuration(self):                                           # Test TTL configuration
        # Create cache with custom TTL
        custom_cache = Open_Router__Chat__Cache()
        custom_cache.cache_ttl_hours = 48
        custom_cache.cache = self.chat_cache.cache                                    # Use same storage

        # Cache a response
        custom_cache.cache_chat_response(self.test_request_simple,
                                        self.test_response_simple)

        # Check TTL in cached entry
        cache_id = custom_cache.generate_cache_id(self.test_request_simple)
        file_id  = Safe_Id(cache_id)
        with custom_cache.cache.fs__latest_temporal.file__json(file_id) as _:
            cached_data = _.content()
            assert cached_data['ttl_hours'] == 48

    def test_cache_with_cost_breakdown(self):                                         # Test caching with cost info
        result = self.chat_cache.cache_chat_response(self.test_request_simple,
                                                     self.test_response_complex)

        assert result is True

        # Verify cost breakdown is preserved
        cached_response = self.chat_cache.get_cached_response(self.test_request_simple)
        assert 'cost_breakdown' in cached_response
        assert cached_response['cost_breakdown']['total_cost'] == 0.0001

    def test_cache_message_order_matters(self):                                       # Test message order affects cache
        messages_1 = [
            {'role': 'user'     , 'content': 'Hello'   },
            {'role': 'assistant', 'content': 'Hi there'},
            {'role': 'user'     , 'content': 'How are you?'}
        ]

        messages_2 = [
            {'role': 'user'     , 'content': 'How are you?'},
            {'role': 'assistant', 'content': 'Hi there'    },
            {'role': 'user'     , 'content': 'Hello'       }
        ]

        request_1 = {'model': 'test', 'messages': messages_1, 'temperature': 0.7, 'max_tokens': 100}
        request_2 = {'model': 'test', 'messages': messages_2, 'temperature': 0.7, 'max_tokens': 100}

        # Different message order should generate different cache IDs
        cache_id_1 = self.chat_cache.generate_cache_id(request_1)
        cache_id_2 = self.chat_cache.generate_cache_id(request_2)
        assert cache_id_1 != cache_id_2

    def test_concurrent_cache_operations(self):                                       # Test multiple concurrent operations
        # Cache multiple different requests
        requests_responses = [
            (self.test_request_simple      , self.test_response_simple ),
            (self.test_request_with_system , self.test_response_complex)
        ]

        for request, response in requests_responses:
            self.chat_cache.cache_chat_response(request, response)

        # All should be retrievable
        for request, expected_response in requests_responses:
            cached = self.chat_cache.get_cached_response(request)
            assert cached == expected_response

    def test_cache_file_structure(self):                                              # Test underlying file structure
        self.chat_cache.cache_chat_response(self.test_request_simple,
                                           self.test_response_simple)

        cache_id = self.chat_cache.generate_cache_id(self.test_request_simple)
        file_id  = Safe_Id(cache_id)
        # Check both latest and temporal paths exist
        with self.chat_cache.cache.fs__latest_temporal.file__json(file_id) as _:
            assert type(_.file__config.file_type) is Memory_FS__File__Type__Json
            assert len(_.file__config.file_paths) == 2                                # Latest + temporal
            assert 'latest' in _.file__config.file_paths[0]

            # Verify file exists in storage
            assert _.exists() is True