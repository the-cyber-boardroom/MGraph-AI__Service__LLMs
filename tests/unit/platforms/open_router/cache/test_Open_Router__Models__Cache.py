from unittest                                                                                               import TestCase
from memory_fs.file_fs.File_FS                                                                              import File_FS
from osbot_aws.aws.s3.S3                                                                                    import S3
from osbot_aws.testing.Temp__Random__AWS_Credentials                                                        import OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID, OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION
from osbot_aws.utils.AWS_Sanitization                                                                       import str_to_valid_s3_bucket_name
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_int                                                              import Safe_Int
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                                     import Safe_Str
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                                          import Safe_Id
from osbot_utils.utils.Misc                                                                                 import random_string_short, list_set
from osbot_utils.utils.Objects                                                                              import base_classes
from osbot_aws.AWS_Config                                                                                   import aws_config
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache                                  import Open_Router__Cache
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Models__Cache                          import Open_Router__Models__Cache
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Description                import Safe_Str__Open_Router__Description
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Modality                   import Safe_Str__Open_Router__Modality
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_ID                   import Safe_Str__Open_Router__Model_ID
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_Name                 import Safe_Str__Open_Router__Model_Name
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_Slug                 import Safe_Str__Open_Router__Model_Slug
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Parameter                  import Safe_Str__Open_Router__Parameter
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Tokenizer                  import Safe_Str__Open_Router__Tokenizer
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model                 import Schema__Open_Router__Model
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Pricing__Float import Schema__Open_Router__Model__Pricing__Float
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Models__Response      import Schema__Open_Router__Models__Response
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Architecture   import Schema__Open_Router__Model__Architecture
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Pricing        import Schema__Open_Router__Model__Pricing
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model__Top_Provider   import Schema__Open_Router__Model__Top_Provider
from tests.unit.Service__Fast_API__Test_Objs                                                                import setup__service_fast_api_test_objs


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
            id                    = Safe_Str__Open_Router__Model_ID("provider/model-1")       ,
            canonical_slug        = Safe_Str__Open_Router__Model_Slug("model-1-slug")         ,
            name                  = Safe_Str__Open_Router__Model_Name("Test Model 1")         ,
            created               = Safe_Int(1700000000)                                      ,
            description           = Safe_Str__Open_Router__Description("Test model description"),
            context_length        = Safe_Int(4096)                                            ,
            architecture          = Schema__Open_Router__Model__Architecture(
                modality          = Safe_Str__Open_Router__Modality("text->text")            ,
                input_modalities  = [Safe_Str("text")]                                       ,
                output_modalities = [Safe_Str("text")]                                       ,
                tokenizer         = Safe_Str__Open_Router__Tokenizer("Test")
            ),
            pricing = Schema__Open_Router__Model__Pricing(
                prompt     = Schema__Open_Router__Model__Pricing__Float("0.001")             ,
                completion = Schema__Open_Router__Model__Pricing__Float("0.002")
            ),
            top_provider = Schema__Open_Router__Model__Top_Provider(
                context_length = Safe_Int(4096)                                              ,
                is_moderated   = False
            ),
            supported_parameters = [Safe_Str__Open_Router__Parameter("temperature")          ,
                                    Safe_Str__Open_Router__Parameter("max_tokens")]
        )

        cls.test_model_2 = Schema__Open_Router__Model(
            id                    = Safe_Str__Open_Router__Model_ID("provider/model-2")       ,
            canonical_slug        = Safe_Str__Open_Router__Model_Slug("model-2-slug")         ,
            name                  = Safe_Str__Open_Router__Model_Name("Test Model 2")         ,
            created               = Safe_Int(1700000001)                                      ,
            description           = Safe_Str__Open_Router__Description("Another test model")  ,
            context_length        = Safe_Int(8192)                                            ,
            architecture          = Schema__Open_Router__Model__Architecture(
                modality          = Safe_Str__Open_Router__Modality("text->text")            ,
                input_modalities  = [Safe_Str("text")]                                       ,
                output_modalities = [Safe_Str("text")]                                       ,
                tokenizer         = Safe_Str__Open_Router__Tokenizer("Test")
            ),
            pricing = Schema__Open_Router__Model__Pricing(
                prompt     = Schema__Open_Router__Model__Pricing__Float("0.002")             ,
                completion = Schema__Open_Router__Model__Pricing__Float("0.004")
            ),
            top_provider = Schema__Open_Router__Model__Top_Provider(
                context_length = Safe_Int(8192)                                              ,
                is_moderated   = False
            ),
            supported_parameters = [Safe_Str__Open_Router__Parameter("temperature")          ,
                                    Safe_Str__Open_Router__Parameter("max_tokens")           ,
                                    Safe_Str__Open_Router__Parameter("top_p")]
        )

        cls.test_models_response = Schema__Open_Router__Models__Response(
            data = [cls.test_model_1, cls.test_model_2]
        )

        cls.test_bucket    = str_to_valid_s3_bucket_name(random_string_short("test-models-cache-"))
        cls.cache          = Open_Router__Cache        (s3__bucket = cls.test_bucket).setup()
        cls.models_cache   = Open_Router__Models__Cache(cache      = cls.cache      ).setup()

    @classmethod
    def tearDownClass(cls):
        with cls.cache.s3__storage.s3 as _:
            _.bucket_delete_all_files(cls.test_bucket)
            _.bucket_delete          (cls.test_bucket)


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
        assert type(cache.cache)       is Open_Router__Cache
        assert cache.cache.s3__storage is not None

    def test_cache_models_response(self):                                               # Test caching models response
        cache__file_fs = self.models_cache.cache_models_response(self.test_models_response)
        with cache__file_fs as _:
            assert type(_)                                           is File_FS
            assert _.exists()                                        is True
            assert _.content ()                                      == self.test_models_response.json()
            assert list_set(_.metadata().data)                       == ['cache_timestamp', 'cache_ttl_hours']
            assert _.metadata().data.get(Safe_Id('cache_ttl_hours')) == 6

        with self.models_cache.get_cached_models() as _:
            assert type(_) is Schema__Open_Router__Models__Response
            assert _.json() == self.test_models_response.json()