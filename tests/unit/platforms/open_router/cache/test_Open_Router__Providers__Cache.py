from datetime                                                                        import datetime, timedelta
from unittest                                                                        import TestCase
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path       import Safe_Str__File__Path
from osbot_utils.utils.Objects                                                       import base_classes
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache           import Open_Router__Cache
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Providers__Cache import Open_Router__Providers__Cache
from mgraph_ai_service_llms.service.s3.Storage_FS__S3                                import Storage_FS__S3
from tests.unit.Service__Fast_API__Test_Objs                                         import setup__service_fast_api_test_objs


class test_Open_Router__Providers__Cache(TestCase):                                     # Test providers cache implementation

    @classmethod
    def setUpClass(cls):                                                                # Initialize test data
        cls.test_objs = setup__service_fast_api_test_objs()

        cls.test_providers_data = {
            "data": [
                {
                    "id"          : "openai"                      ,
                    "name"        : "OpenAI"                      ,
                    "description" : "OpenAI provider"             ,
                    "status"      : "operational"                 ,
                    "models"      : ["gpt-4", "gpt-3.5-turbo"]    ,
                    "capabilities": ["chat", "completion"]
                },
                {
                    "id"          : "anthropic"                   ,
                    "name"        : "Anthropic"                   ,
                    "description" : "Anthropic provider"          ,
                    "status"      : "operational"                 ,
                    "models"      : ["claude-3", "claude-2.1"]    ,
                    "capabilities": ["chat", "completion", "vision"]
                },
                {
                    "id"          : "groq"                        ,
                    "name"        : "Groq"                        ,
                    "description" : "Groq high-speed inference"   ,
                    "status"      : "operational"                 ,
                    "models"      : ["mixtral-8x7b", "llama-2-70b"],
                    "capabilities": ["chat", "completion"]
                }
            ]
        }

        cls.test_provider_status = {
            "id"              : "openai"                         ,
            "status"          : "operational"                    ,
            "response_time_ms": 250                              ,
            "uptime_percent"  : 99.9                             ,
            "last_checked"    : datetime.now().isoformat()
        }

    def setUp(self):                                                                    # Create fresh cache for each test
        self.providers_cache = Open_Router__Providers__Cache()

        # Mock the Open_Router__Cache
        self.mock_cache = Mock(spec=Open_Router__Cache)
        self.mock_cache.save_to_both          = Mock(return_value=True)
        self.mock_cache.save_to_latest        = Mock(return_value=True)
        self.mock_cache.save_to_temporal      = Mock(return_value=True)
        self.mock_cache.load_from_latest      = Mock(return_value=None)
        self.mock_cache.get_latest_metadata   = Mock(return_value=None)
        self.mock_cache.list_temporal_entries = Mock(return_value=[])
        self.mock_cache.clear_all             = Mock(return_value=True)
        self.mock_cache.clear_old_temporal    = Mock(return_value=0)
        self.mock_cache.s3_prefix              = "test-providers"

        # Mock storage_fs
        self.mock_storage = Mock(spec=Storage_FS__S3)
        self.mock_storage.file__json    = Mock(return_value=None)
        self.mock_storage.folder__files = Mock(return_value=[])

        self.mock_cache.storage_fs = self.mock_storage

        self.providers_cache.cache = self.mock_cache

    def test__init__(self):                                                             # Test initialization
        cache = Open_Router__Providers__Cache()

        assert type(cache)           is Open_Router__Providers__Cache
        assert base_classes(cache)   == [Type_Safe, object]
        assert cache.cache           is None
        assert cache.cache_ttl_hours == 24                                              # Providers have longer TTL

    def test_setup(self):                                                               # Test setup process
        with patch('mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Providers__Cache.Open_Router__Cache') as MockCache:
            mock_instance = Mock(spec=Open_Router__Cache)
            MockCache.return_value = mock_instance
            mock_instance.setup = Mock(return_value=mock_instance)
            mock_instance.s3_prefix = "providers"

            cache  = Open_Router__Providers__Cache()
            result = cache.setup()

            assert result is cache
            assert cache.cache is mock_instance
            assert cache.cache.s3_prefix == "providers"
            mock_instance.setup.assert_called_once()

    def test_cache_providers_response(self):                                            # Test caching providers data
        timestamp = datetime.now()

        with patch('mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Providers__Cache.datetime') as mock_datetime:
            mock_datetime.now.return_value = timestamp

            result = self.providers_cache.cache_providers_response(self.test_providers_data.copy())

            assert result is True

            # Verify save_to_both was called
            self.mock_cache.save_to_both.assert_called_once()
            call_args = self.mock_cache.save_to_both.call_args
            assert call_args[1]['file_id'] == "openrouter-providers"
            assert call_args[1]['timestamp'] == timestamp

            # Verify metadata was added
            saved_data = call_args[1]['data']
            assert '_cache_timestamp' in saved_data
            assert '_cache_ttl_hours' in saved_data
            assert saved_data['_cache_ttl_hours'] == 24
            assert saved_data['_cache_timestamp'] == timestamp.isoformat()

    def test_get_cached_providers(self):                                                # Test retrieving cached providers
        cached_data = {
            "data": self.test_providers_data['data']    ,
            "_cache_timestamp": datetime.now().isoformat()
        }

        self.mock_cache.load_from_latest = Mock(return_value=cached_data)

        result = self.providers_cache.get_cached_providers()

        assert result == cached_data
        self.mock_cache.load_from_latest.assert_called_once_with("openrouter-providers")

    def test_get_cached_providers_adds_metadata(self):                                  # Test metadata addition
        cached_data = {"data": self.test_providers_data['data']}

        mock_metadata = {"timestamp": datetime.now().isoformat()}

        self.mock_cache.load_from_latest    = Mock(return_value=cached_data)
        self.mock_cache.get_latest_metadata = Mock(return_value=mock_metadata)

        result = self.providers_cache.get_cached_providers()

        assert '_cache_timestamp' in result
        assert result['_cache_timestamp'] == mock_metadata['timestamp']

    def test_get_cached_providers_none(self):                                           # Test when no cache exists
        self.mock_cache.load_from_latest = Mock(return_value=None)

        result = self.providers_cache.get_cached_providers()

        assert result is None

    def test_is_cache_valid_true(self):                                                 # Test valid cache
        cached_data = {
            "_cache_timestamp": datetime.now().isoformat()    ,
            "_cache_ttl_hours": 24
        }

        result = self.providers_cache.is_cache_valid(cached_data)

        assert result is True

    def test_is_cache_valid_expired(self):                                              # Test expired cache
        old_timestamp = datetime.now() - timedelta(hours=25)
        cached_data = {
            "_cache_timestamp": old_timestamp.isoformat()     ,
            "_cache_ttl_hours": 24
        }

        result = self.providers_cache.is_cache_valid(cached_data)

        assert result is False

    def test_is_cache_valid_custom_ttl(self):                                           # Test custom TTL in data
        # Cache with custom shorter TTL
        cached_data = {
            "_cache_timestamp": (datetime.now() - timedelta(hours=13)).isoformat(),
            "_cache_ttl_hours": 12  # Custom TTL
        }

        result = self.providers_cache.is_cache_valid(cached_data)

        assert result is False  # Should be expired based on custom TTL

    def test_is_cache_valid_no_timestamp(self):                                         # Test cache without timestamp
        cached_data = {"data": []}

        result = self.providers_cache.is_cache_valid(cached_data)

        assert result is False

    def test_is_cache_valid_invalid_timestamp(self):                                    # Test invalid timestamp format
        cached_data = {
            "_cache_timestamp": "invalid-timestamp"           ,
            "_cache_ttl_hours": 24
        }

        result = self.providers_cache.is_cache_valid(cached_data)

        assert result is False

    def test_is_cache_valid_none(self):                                                 # Test with None
        result = self.providers_cache.is_cache_valid(None)

        assert result is False

    def test_get_providers_with_fallback_uses_cache(self):                              # Test using valid cache
        cached_data = {
            "data": self.test_providers_data['data']          ,
            "_cache_timestamp": datetime.now().isoformat()    ,
            "_cache_ttl_hours": 24
        }

        self.mock_cache.load_from_latest = Mock(return_value=cached_data)

        mock_fetch = Mock()

        result = self.providers_cache.get_providers_with_fallback(mock_fetch)

        # Should not call fetch
        mock_fetch.assert_not_called()

        # Should return cached data
        assert result == cached_data

    def test_get_providers_with_fallback_fetches_fresh(self):                           # Test fetching fresh data
        # No cached data
        self.mock_cache.load_from_latest = Mock(return_value=None)

        # Mock fetch function
        fresh_data = self.test_providers_data.copy()
        mock_fetch = Mock(return_value=fresh_data)

        with patch.object(self.providers_cache, 'cache_providers_response', return_value=True) as mock_cache_method:
            result = self.providers_cache.get_providers_with_fallback(mock_fetch)

            # Should call fetch
            mock_fetch.assert_called_once()

            # Should cache the response
            mock_cache_method.assert_called_once_with(fresh_data)

            # Should return fresh data
            assert result == fresh_data

    def test_get_providers_with_fallback_expired_cache(self):                           # Test with expired cache
        old_timestamp = datetime.now() - timedelta(hours=25)
        cached_data = {
            "data": self.test_providers_data['data']          ,
            "_cache_timestamp": old_timestamp.isoformat()     ,
            "_cache_ttl_hours": 24
        }

        self.mock_cache.load_from_latest = Mock(return_value=cached_data)

        fresh_data = {**self.test_providers_data, "updated": True}
        mock_fetch = Mock(return_value=fresh_data)

        with patch.object(self.providers_cache, 'cache_providers_response'):
            result = self.providers_cache.get_providers_with_fallback(mock_fetch)

            # Should fetch fresh data
            mock_fetch.assert_called_once()

            # Should return fresh data
            assert result == fresh_data

    def test_get_providers_with_fallback_uses_stale(self):                              # Test fallback to stale cache
        # Expired cache
        old_timestamp = datetime.now() - timedelta(hours=25)
        cached_data = {
            "data": self.test_providers_data['data']          ,
            "_cache_timestamp": old_timestamp.isoformat()     ,
            "_cache_ttl_hours": 24
        }

        self.mock_cache.load_from_latest = Mock(return_value=cached_data)

        # Fetch fails
        mock_fetch = Mock(side_effect=Exception("API Error"))

        result = self.providers_cache.get_providers_with_fallback(mock_fetch)

        # Should return stale cache
        assert result == cached_data

    def test_get_providers_with_fallback_no_cache_fetch_fails(self):                    # Test when no cache and fetch fails
        # No cached data
        self.mock_cache.load_from_latest = Mock(return_value=None)

        # Fetch fails
        mock_fetch = Mock(side_effect=Exception("API Error"))

        # Should raise the exception
        with self.assertRaises(Exception) as context:
            self.providers_cache.get_providers_with_fallback(mock_fetch)

        assert str(context.exception) == "API Error"

    def test_get_provider_history(self):                                                # Test getting provider history
        # Set up temporal entries
        self.mock_cache.list_temporal_entries = Mock(return_value=[
            "cache/2025/01/20/10/openrouter-providers.json"       ,
            "cache/2025/01/19/10/openrouter-providers.json"       ,
            "cache/2025/01/18/10/openrouter-providers.json"
        ])

        # Mock file data for each entry
        file_data_1 = {
            "data": self.test_providers_data['data']                    ,
            "_cache_timestamp": "2025-01-20T10:00:00"
        }

        file_data_2 = {
            "data": self.test_providers_data['data'][:2]                ,  # Only 2 providers
            "_cache_timestamp": "2025-01-19T10:00:00"
        }

        file_data_3 = {
            "data": self.test_providers_data['data'][:1]                ,  # Only 1 provider
            "_cache_timestamp": "2025-01-18T10:00:00"
        }

        self.mock_storage.file__json = Mock(side_effect=[file_data_1, file_data_2, file_data_3])

        result = self.providers_cache.get_provider_history(days_back=30)

        assert len(result) == 3
        assert result[0]['timestamp'] == "2025-01-20T10:00:00"
        assert len(result[0]['providers']['data']) == 3
        assert result[1]['timestamp'] == "2025-01-19T10:00:00"
        assert len(result[1]['providers']['data']) == 2
        assert result[2]['timestamp'] == "2025-01-18T10:00:00"
        assert len(result[2]['providers']['data']) == 1

    def test_get_provider_history_empty(self):                                          # Test when no history exists
        self.mock_cache.list_temporal_entries = Mock(return_value=[])

        result = self.providers_cache.get_provider_history(days_back=7)

        assert result == []

    def test_get_provider_history_handles_errors(self):                                 # Test error handling in history
        # Set up temporal entries
        self.mock_cache.list_temporal_entries = Mock(return_value=[
            "cache/2025/01/20/10/openrouter-providers.json"       ,
            "cache/2025/01/19/10/openrouter-providers.json"
        ])

        # First succeeds, second fails
        file_data = {
            "data": self.test_providers_data['data']                    ,
            "_cache_timestamp": "2025-01-20T10:00:00"
        }

        self.mock_storage.file__json = Mock(side_effect=[file_data, Exception("Read error")])

        result = self.providers_cache.get_provider_history(days_back=7)

        # Should only have the successful entry
        assert len(result) == 1
        assert result[0]['timestamp'] == "2025-01-20T10:00:00"

    def test_cache_provider_status(self):                                               # Test caching individual provider status
        provider_id = "openai"
        timestamp   = datetime.now()

        with patch('mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Providers__Cache.datetime') as mock_datetime:
            mock_datetime.now.return_value = timestamp

            # Mock Memory_FS__Latest
            with patch('mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Providers__Cache.Memory_FS__Latest') as MockFS:
                mock_fs = Mock()
                MockFS.return_value = mock_fs

                mock_handler = Mock()
                mock_fs.path_handlers = [mock_handler]

                mock_file = Mock()
                mock_file.create = Mock(return_value=True)
                mock_file.save   = Mock(return_value=True)
                mock_fs.file__json = Mock(return_value=mock_file)

                result = self.providers_cache.cache_provider_status(provider_id, self.test_provider_status)

                assert result is True

                # Verify file was created with correct ID
                mock_fs.file__json.assert_called_once()
                call_args = mock_fs.file__json.call_args
                assert str(call_args[0][0]) == provider_id

                # Verify save was called with metadata
                mock_file.save.assert_called_once()
                save_data = mock_file.save.call_args[0][0]
                assert save_data['_cache_timestamp'] == timestamp.isoformat()
                assert save_data['_cache_ttl_hours'] == 1  # Status has shorter TTL

    def test_get_provider_status(self):                                                 # Test getting cached provider status
        provider_id = "openai"

        # Mock Memory_FS__Latest
        with patch('mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Providers__Cache.Memory_FS__Latest') as MockFS:
            mock_fs = Mock()
            MockFS.return_value = mock_fs

            mock_handler = Mock()
            mock_fs.path_handlers = [mock_handler]

            mock_file = Mock()
            mock_file.exists  = Mock(return_value=True)
            mock_file.content = Mock(return_value=self.test_provider_status)
            mock_fs.file__json = Mock(return_value=mock_file)

            result = self.providers_cache.get_provider_status(provider_id)

            assert result == self.test_provider_status

            # Verify correct path was configured
            assert mock_handler.prefix_path == Safe_Str__File__Path("cache/providers/status")

    def test_get_provider_status_not_exists(self):                                      # Test getting non-existent status
        provider_id = "non-existent"

        # Mock Memory_FS__Latest
        with patch('mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Providers__Cache.Memory_FS__Latest') as MockFS:
            mock_fs = Mock()
            MockFS.return_value = mock_fs

            mock_handler = Mock()
            mock_fs.path_handlers = [mock_handler]

            mock_file = Mock()
            mock_file.exists = Mock(return_value=False)
            mock_fs.file__json = Mock(return_value=mock_file)

            result = self.providers_cache.get_provider_status(provider_id)

            assert result is None

    def test_clear_provider_cache(self):                                                # Test clearing all provider cache
        result = self.providers_cache.clear_provider_cache()

        assert result is True
        self.mock_cache.clear_all.assert_called_once()

    def test_cleanup_old_provider_cache(self):                                          # Test cleaning old provider data
        self.mock_cache.clear_old_temporal = Mock(return_value=8)

        result = self.providers_cache.cleanup_old_provider_cache(days_to_keep=60)

        assert result == 8
        self.mock_cache.clear_old_temporal.assert_called_once_with(60)

    def test_cleanup_old_provider_cache_default_days(self):                             # Test cleanup with default days
        self.mock_cache.clear_old_temporal = Mock(return_value=3)

        result = self.providers_cache.cleanup_old_provider_cache()

        assert result == 3
        self.mock_cache.clear_old_temporal.assert_called_once_with(60)  # Default is 60 days

    def test_provider_cache_ttl_longer_than_models(self):                               # Test TTL is appropriate
        providers_cache = Open_Router__Providers__Cache()

        # Import models cache to compare
        from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Models__Cache import Open_Router__Models__Cache
        models_cache = Open_Router__Models__Cache()

        # Providers should have longer TTL since they change less frequently
        assert providers_cache.cache_ttl_hours > models_cache.cache_ttl_hours
        assert providers_cache.cache_ttl_hours == 24
        assert models_cache.cache_ttl_hours    == 6

    def test_provider_status_ttl_shorter(self):                                         # Test status has shorter TTL
        provider_id   = "test-provider"
        status_data   = {"status": "operational"}

        with patch('mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Providers__Cache.Memory_FS__Latest'):
            with patch.object(self.providers_cache, 'cache') as mock_cache:
                mock_cache.storage_fs = Mock()

                # Create a mock file that tracks save calls
                save_calls = []

                def mock_save(data):
                    save_calls.append(data)
                    return True

                mock_file = Mock()
                mock_file.create = Mock(return_value=True)
                mock_file.save   = mock_save

                with patch('memory_fs.Memory_FS__Latest.Memory_FS__Latest.file__json', return_value=mock_file):
                    self.providers_cache.cache_provider_status(provider_id, status_data)

                    # Verify TTL is 1 hour for status
                    if save_calls:
                        assert save_calls[0]['_cache_ttl_hours'] == 1