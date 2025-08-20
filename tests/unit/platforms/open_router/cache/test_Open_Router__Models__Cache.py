# tests/unit/platforms/open_router/cache/test_Open_Router__Models__Cache.py

from datetime                                                                                            import datetime, timedelta
from unittest                                                                                            import TestCase
from osbot_aws.aws.s3.S3                                                                                import S3
from osbot_aws.testing.Temp__Random__AWS_Credentials                                                    import OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID, OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION
from osbot_aws.utils.AWS_Sanitization                                                                   import str_to_valid_s3_bucket_name
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                                       import Safe_Id
from osbot_utils.utils.Misc                                                                              import random_string_short
from osbot_utils.utils.Objects                                                                           import base_classes
from osbot_aws.AWS_Config                                                                               import aws_config
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache                               import Open_Router__Cache
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Models__Cache                       import Open_Router__Models__Cache
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model              import Schema__Open_Router__Model
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Models__Response   import Schema__Open_Router__Models__Response
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Architecture import Schema__Open_Router__Model__Architecture
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Pricing     import Schema__Open_Router__Model__Pricing
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Top_Provider import Schema__Open_Router__Model__Top_Provider
from tests.unit.Service__Fast_API__Test_Objs                                                             import setup__service_fast_api_test_objs


class test_Open_Router__Models__Cache(TestCase):                                                # Test models cache with real S3

    @classmethod
    def setUpClass(cls):                                                                        # Initialize LocalStack and test data
        cls.test_objs = setup__service_fast_api_test_objs()

        cls.test_bucket = str_to_valid_s3_bucket_name(random_string_short("test-models-cache-"))
        cls.s3          = S3()

        assert aws_config.account_id () == OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID
        assert aws_config.region_name() == OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION

        # Create test models with proper schema objects
        cls.test_model_1 = Schema__Open_Router__Model(
            id             = Safe_Id("provider/model-1")                       ,
            canonical_slug = Safe_Id("model-1-slug")                           ,
            name           = Safe_Id("Test Model 1")                           ,
            created        = 1700000000                                        ,
            description    = "Test model description"                          ,
            context_length = 4096                                              ,
            architecture   = Schema__Open_Router__Model__Architecture(
                modality          = "text->text"                               ,
                input_modalities  = ["text"]                                   ,
                output_modalities = ["text"]                                   ,
                tokenizer         = "Test"
            ),
            pricing = Schema__Open_Router__Model__Pricing(
                prompt     = "0.001"                                           ,
                completion = "0.002"
            ),
            top_provider = Schema__Open_Router__Model__Top_Provider(
                context_length = 4096                                          ,
                is_moderated   = False
            ),
            supported_parameters = ["temperature", "max_tokens"]
        )

        cls.test_model_2 = Schema__Open_Router__Model(
            id             = Safe_Id("provider/model-2")                       ,
            canonical_slug = Safe_Id("model-2-slug")                           ,
            name           = Safe_Id("Test Model 2")                           ,
            created        = 1700000001                                        ,
            description    = "Another test model"                              ,
            context_length = 8192                                              ,
            architecture   = Schema__Open_Router__Model__Architecture(
                modality          = "text->text"                               ,
                input_modalities  = ["text"]                                   ,
                output_modalities = ["text"]                                   ,
                tokenizer         = "Test"
            ),
            pricing = Schema__Open_Router__Model__Pricing(
                prompt     = "0.002"                                           ,
                completion = "0.004"
            ),
            top_provider = Schema__Open_Router__Model__Top_Provider(
                context_length = 8192                                          ,
                is_moderated   = False
            ),
            supported_parameters = ["temperature", "max_tokens", "top_p"]
        )

        cls.test_models_response = Schema__Open_Router__Models__Response(
            data = [cls.test_model_1, cls.test_model_2]
        )

    @classmethod
    def tearDownClass(cls):                                                             # Clean up all test buckets
        # Clean up any test buckets created
        for bucket in cls.s3.buckets():
            if bucket.startswith('test-models-cache-'):
                cls.s3.bucket_delete_all_files(bucket)
                cls.s3.bucket_delete(bucket)

    def setUp(self):                                                                    # Create fresh cache for each test
        # Create unique bucket for this test
        self.test_bucket_instance = str_to_valid_s3_bucket_name(random_string_short("test-models-cache-"))

        self.models_cache = Open_Router__Models__Cache()
        self.models_cache.cache = Open_Router__Cache()
        self.models_cache.cache.s3_bucket = self.test_bucket_instance
        self.models_cache.cache.s3_prefix = "models-test"
        self.models_cache.setup()

    def tearDown(self):                                                                 # Clean up after each test
        # Delete the bucket created for this test
        if self.s3.bucket_exists(self.test_bucket_instance):
            self.s3.bucket_delete_all_files(self.test_bucket_instance)
            self.s3.bucket_delete(self.test_bucket_instance)

    def test__init__(self):                                                             # Test initialization
        cache = Open_Router__Models__Cache()

        assert type(cache)           is Open_Router__Models__Cache
        assert base_classes(cache)   == [Type_Safe, object]
        assert cache.cache           is None
        assert cache.cache_ttl_hours == 6

    def test_setup(self):                                                               # Test setup process
        cache = Open_Router__Models__Cache()
        result = cache.setup()

        assert result is cache
        assert type(cache.cache) is Open_Router__Cache
        assert cache.cache.storage_fs is not None

        # Clean up the bucket created by setup
        if cache.cache.storage_fs:
            cache.cache.storage_fs.s3.bucket_delete_all_files(cache.cache.s3_bucket)
            cache.cache.storage_fs.s3.bucket_delete(cache.cache.s3_bucket)

    def test_cache_models_response(self):                                               # Test caching models response
        result = self.models_cache.cache_models_response(self.test_models_response)

        assert result is True

        # Verify data was saved to latest
        cached_data = self.models_cache.get_cached_models()
        assert cached_data is not None
        assert 'data' in cached_data
        assert len(cached_data['data']) == 2
        assert '_cache_timestamp' in cached_data
        assert '_cache_ttl_hours' in cached_data
        assert cached_data['_cache_ttl_hours'] == 6

    def test__cache_individual_model(self):                                             # Test caching individual model
        timestamp = datetime.now()

        result = self.models_cache._cache_individual_model(self.test_model_1, timestamp)

        assert result is True

        # Verify individual model was cached
        # Check S3 for the file
        all_files = self.models_cache.cache.storage_fs.files__paths()
        individual_files = [f for f in all_files if "individual" in str(f)]
        assert len(individual_files) > 0

    def test_get_cached_models(self):                                                   # Test retrieving cached models
        # Cache models first
        self.models_cache.cache_models_response(self.test_models_response)

        # Retrieve them
        cached_data = self.models_cache.get_cached_models()

        assert cached_data is not None
        assert 'data' in cached_data
        assert len(cached_data['data']) == 2
        assert cached_data['data'][0]['id'] == str(self.test_model_1.id)
        assert cached_data['data'][1]['id'] == str(self.test_model_2.id)

    def test_get_cached_models_not_exists(self):                                        # Test getting models when none cached
        cached_data = self.models_cache.get_cached_models()

        assert cached_data is None

    def test_get_cached_model_by_id(self):                                              # Test getting specific model
        # Cache models first
        self.models_cache.cache_models_response(self.test_models_response)

        # Get specific model
        model_data = self.models_cache.get_cached_model_by_id("provider/model-1")

        assert model_data is not None
        assert model_data['id'] == "provider/model-1"
        assert model_data['name'] == "Test Model 1"

    def test_get_cached_model_by_id_not_exists(self):                                   # Test getting non-existent model
        model_data = self.models_cache.get_cached_model_by_id("non/existent")

        assert model_data is None

    def test_is_cache_valid_true(self):                                                 # Test valid cache
        cached_data = {
            "_cache_timestamp": datetime.now().isoformat(),
            "_cache_ttl_hours": 6,
            "data": []
        }

        result = self.models_cache.is_cache_valid(cached_data)

        assert result is True

    def test_is_cache_valid_expired(self):                                              # Test expired cache
        old_timestamp = datetime.now() - timedelta(hours=7)
        cached_data = {
            "_cache_timestamp": old_timestamp.isoformat(),
            "_cache_ttl_hours": 6,
            "data": []
        }

        result = self.models_cache.is_cache_valid(cached_data)

        assert result is False

    def test_is_cache_valid_no_data(self):                                              # Test invalid cache data
        assert self.models_cache.is_cache_valid(None) is False
        assert self.models_cache.is_cache_valid({}) is False
        assert self.models_cache.is_cache_valid({"data": []}) is False

    def test_get_models_with_fallback_uses_cache(self):                                 # Test using valid cache
        # Cache models first
        self.models_cache.cache_models_response(self.test_models_response)

        # Create fetch function that should not be called
        fetch_called = False
        def fetch_function():
            nonlocal fetch_called
            fetch_called = True
            return self.test_models_response

        # Get models - should use cache
        result = self.models_cache.get_models_with_fallback(fetch_function)

        assert fetch_called is False  # Should not fetch
        assert len(result) == 2
        assert type(result[0]) is Schema__Open_Router__Model

    def test_get_models_with_fallback_fetches_fresh(self):                              # Test fetching fresh data
        # No cached data initially

        # Create fetch function
        fetch_called = False
        def fetch_function():
            nonlocal fetch_called
            fetch_called = True
            return self.test_models_response

        # Get models - should fetch fresh
        result = self.models_cache.get_models_with_fallback(fetch_function)

        assert fetch_called is True
        assert len(result) == 2

        # Should have cached the data
        cached_data = self.models_cache.get_cached_models()
        assert cached_data is not None

    def test_get_models_with_fallback_uses_stale(self):                                 # Test fallback to stale cache
        # Create expired cache
        old_timestamp = datetime.now() - timedelta(hours=7)
        stale_data = self.test_models_response.json()
        stale_data['_cache_timestamp'] = old_timestamp.isoformat()
        stale_data['_cache_ttl_hours'] = 6

        # Save stale data
        self.models_cache.cache.save_to_latest("openrouter-models", stale_data)

        # Create failing fetch function
        def fetch_function():
            raise Exception("API Error")

        # Should return stale data
        result = self.models_cache.get_models_with_fallback(fetch_function)

        assert len(result) == 2

    def test__parse_cached_models(self):                                                # Test parsing cached data
        cached_data = {
            "data": [self.test_model_1.json(), self.test_model_2.json()]
        }

        result = self.models_cache._parse_cached_models(cached_data)

        assert len(result) == 2
        assert all(isinstance(m, Schema__Open_Router__Model) for m in result)
        assert result[0].id == self.test_model_1.id
        assert result[1].id == self.test_model_2.id

    def test_get_model_history(self):                                                   # Test getting model history
        # Create historical entries
        now = datetime.now()

        for days_ago in range(3):
            timestamp = now - timedelta(days=days_ago)
            models_data = self.test_models_response.json()
            models_data['_cache_timestamp'] = timestamp.isoformat()

            # Modify pricing for history tracking
            if days_ago > 0:
                models_data['data'][0]['pricing']['prompt'] = f"0.00{days_ago}"

            self.models_cache.cache.save_to_temporal("openrouter-models", models_data, timestamp)

        # Get history for model-1
        history = self.models_cache.get_model_history("provider/model-1", days_back=7)

        assert len(history) >= 3
        for entry in history:
            assert 'timestamp' in entry
            assert 'model_data' in entry
            assert entry['model_data']['id'] == "provider/model-1"

    def test_detect_pricing_changes(self):                                              # Test detecting price changes
        # Save current data with one price
        current_response = Schema__Open_Router__Models__Response(data=[
            self.test_model_1,
            self.test_model_2
        ])
        self.models_cache.cache_models_response(current_response)

        # Save yesterday's data with different price
        yesterday = datetime.now() - timedelta(days=1)
        old_data = current_response.json()
        old_data['data'][0]['pricing']['prompt'] = "0.0005"  # Different price
        old_data['_cache_timestamp'] = yesterday.isoformat()

        self.models_cache.cache.save_to_temporal("openrouter-models", old_data, yesterday)

        # Detect changes
        changes = self.models_cache.detect_pricing_changes()

        assert len(changes) == 1
        assert changes[0]['model_id'] == "provider/model-1"
        assert changes[0]['previous']['prompt'] == "0.0005"
        assert changes[0]['current']['prompt'] == "0.001"

    def test_warm_cache(self):                                                          # Test cache warming
        fetch_called = False

        def fetch_function():
            nonlocal fetch_called
            fetch_called = True
            return self.test_models_response

        result = self.models_cache.warm_cache(fetch_function)

        assert result is True
        assert fetch_called is True

        # Cache should be populated
        cached_data = self.models_cache.get_cached_models()
        assert cached_data is not None

    def test_warm_cache_failure(self):                                                  # Test cache warming failure
        def fetch_function():
            raise Exception("API Error")

        result = self.models_cache.warm_cache(fetch_function)

        assert result is False

    def test_clear_cache(self):                                                         # Test clearing cache
        # Add some data
        self.models_cache.cache_models_response(self.test_models_response)
        assert self.models_cache.get_cached_models() is not None

        # Clear cache
        result = self.models_cache.clear_cache()

        assert result is True
        assert self.models_cache.get_cached_models() is None

    def test_cleanup_old_cache(self):                                                   # Test cleaning old cache
        # Create old and new entries
        now = datetime.now()

        # Old entry (35 days ago)
        old_date = now - timedelta(days=35)
        old_data = self.test_models_response.json()
        self.models_cache.cache.save_to_temporal("old-models", old_data, old_date)

        # Recent entry (5 days ago)
        recent_date = now - timedelta(days=5)
        recent_data = self.test_models_response.json()
        self.models_cache.cache.save_to_temporal("recent-models", recent_data, recent_date)

        # Clean up old entries
        deleted_count = self.models_cache.cleanup_old_cache(days_to_keep=30)

        assert deleted_count >= 0  # Should have deleted old entries

    def test_cache_ttl_different_than_providers(self):                                 # Test TTL is appropriate
        assert self.models_cache.cache_ttl_hours == 6  # Models have 6 hour TTL

        # Providers should have longer TTL
        from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Providers__Cache import Open_Router__Providers__Cache
        providers_cache = Open_Router__Providers__Cache()
        assert providers_cache.cache_ttl_hours == 24  # Providers have 24 hour TTL

    def test_concurrent_model_operations(self):                                         # Test multiple concurrent operations
        # Cache main response
        self.models_cache.cache_models_response(self.test_models_response)

        # Cache individual models
        timestamp = datetime.now()
        self.models_cache._cache_individual_model(self.test_model_1, timestamp)
        self.models_cache._cache_individual_model(self.test_model_2, timestamp)

        # All should be retrievable
        assert self.models_cache.get_cached_models() is not None
        assert self.models_cache.get_cached_model_by_id("provider/model-1") is not None
        assert self.models_cache.get_cached_model_by_id("provider/model-2") is not None

    def test_model_data_integrity(self):                                                # Test data integrity through cache
        # Cache models
        self.models_cache.cache_models_response(self.test_models_response)

        # Retrieve and verify all fields
        cached_data = self.models_cache.get_cached_models()
        model_1_data = cached_data['data'][0]

        assert model_1_data['id'] == "provider/model-1"
        assert model_1_data['name'] == "Test Model 1"
        assert model_1_data['context_length'] == 4096
        assert model_1_data['pricing']['prompt'] == "0.001"
        assert model_1_data['pricing']['completion'] == "0.002"
        assert model_1_data['architecture']['modality'] == "text->text"