from datetime                                                                           import datetime
from unittest                                                                           import TestCase
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                      import Safe_Id
from memory_fs.file_fs.File_FS                                                          import File_FS
from osbot_aws.aws.s3.S3                                                                import S3
from osbot_aws.testing.Temp__Random__AWS_Credentials                                    import OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID, OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION
from osbot_aws.utils.AWS_Sanitization                                                   import str_to_valid_s3_bucket_name
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now                            import Timestamp_Now
from osbot_utils.utils.Misc                                                             import random_string_short, list_set
from osbot_utils.utils.Objects                                                          import base_classes
from osbot_aws.AWS_Config                                                               import aws_config
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache              import Open_Router__Cache
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Models__Cache      import Open_Router__Models__Cache
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Providers__Cache   import Open_Router__Providers__Cache, FILE_ID__OPEN_ROUTER__PROVIDERS
from tests.unit.Service__Fast_API__Test_Objs                                            import setup__service_fast_api_test_objs


class test_Open_Router__Providers__Cache(TestCase):                                      # Test providers cache implementation

    @classmethod
    def setUpClass(cls):                                                                  # Initialize LocalStack and test data
        cls.test_objs = setup__service_fast_api_test_objs()

        cls.test_bucket = str_to_valid_s3_bucket_name(random_string_short("test-providers-cache-"))
        cls.s3          = S3()

        assert aws_config.account_id () == OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID
        assert aws_config.region_name() == OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION

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

        cls.cache          = Open_Router__Cache        (s3__bucket = cls.test_bucket, s3__prefix="providers").setup()
        cls.providers_cache = Open_Router__Providers__Cache(cache = cls.cache).setup()

    @classmethod
    def tearDownClass(cls):
        with cls.cache.s3__storage.s3 as _:
            _.bucket_delete_all_files(cls.test_bucket)
            _.bucket_delete          (cls.test_bucket)

    def tearDown(self):                                                                  # Clean up after each test
        self.cache.clear_all()

    def test__init__(self):                                                              # Test initialization
        cache = Open_Router__Providers__Cache()

        assert type(cache)           is Open_Router__Providers__Cache
        assert base_classes(cache)   == [Type_Safe, object]
        assert cache.cache           is None
        assert cache.cache_ttl_hours == 24                                               # Providers have longer TTL

    def test_setup(self):                                                                # Test setup process
        cache = Open_Router__Providers__Cache()
        result = cache.setup()

        assert result is cache
        assert type(cache.cache)       is Open_Router__Cache
        assert cache.cache.s3__storage is not None
        assert cache.cache.s3__prefix  == "providers"

    def test_cache_providers_response(self):                                             # Test caching providers data
        cache__file_fs = self.providers_cache.cache_providers_response(self.test_providers_data.copy())

        with cache__file_fs as _:
            assert type(_)                                           is File_FS
            assert _.exists()                                        is True
            assert _.content()                                       == self.test_providers_data
            assert list_set(_.metadata().data)                       == ['cache_timestamp', 'cache_ttl_hours']
            assert _.metadata().data.get(Safe_Id('cache_ttl_hours')) == 24

        cached_data = self.providers_cache.get_cached_providers()           # Verify we can retrieve it
        assert cached_data == self.test_providers_data

    def test_get_cached_providers_none(self):                                            # Test when no cache exists
        result = self.providers_cache.get_cached_providers()
        assert result is None

    def test_is_cache_valid_true(self):                                                  # Test valid cache

        self.providers_cache.cache_providers_response(self.test_providers_data)         # Cache data with current timestamp

        result = self.providers_cache.is_cache_valid()
        assert result is True

    def test_is_cache_valid_expired(self):                                               # Test expired cache
        # Cache data
        cache__file_fs = self.providers_cache.cache_providers_response(self.test_providers_data)

        # Manually set old timestamp in metadata
        old_timestamp = Timestamp_Now() - (25 * 3600)  # 25 hours ago
        with cache__file_fs as _:
            _.metadata__update({'cache_timestamp': old_timestamp})

        result = self.providers_cache.is_cache_valid()
        assert result is False

    def test_is_cache_valid_no_cache(self):                                              # Test with no cache
        result = self.providers_cache.is_cache_valid()
        assert result is False


    def test_provider_cache_ttl_longer_than_models(self):                                # Test TTL is appropriate
        providers_cache = Open_Router__Providers__Cache()
        models_cache    = Open_Router__Models__Cache()

        # Providers should have longer TTL since they change less frequently
        assert providers_cache.cache_ttl_hours > models_cache.cache_ttl_hours
        assert providers_cache.cache_ttl_hours == 24
        assert models_cache.cache_ttl_hours    == 6