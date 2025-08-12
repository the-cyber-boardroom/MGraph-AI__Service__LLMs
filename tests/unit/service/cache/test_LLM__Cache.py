from unittest                                           import TestCase

from osbot_aws.aws.s3.S3__DB_Base import S3__DB_Base

from mgraph_ai_service_llms.service.cache.LLM__Cache    import LLM__Cache
from tests.unit.Service__Fast_API__Test_Objs            import setup__service_fast_api_test_objs


class test_LLM__Cache(TestCase):

    @classmethod
    def setUpClass(cls):
        setup__service_fast_api_test_objs()
        cls.llm_cache = LLM__Cache()

    def test__SetUpClass(self):
        with self.llm_cache as _:
            assert type(_      ) is LLM__Cache
            assert type(_.s3_db) is S3__DB_Base
            assert _.root_folder == 'llm-service-cache/'

    def test_setup(self):
        with self.llm_cache.setup().s3_db as _:
            assert type(_) is S3__DB_Base
            assert _.bucket_name__prefix == 'mgraph-ai-llms'
            assert _.bucket_name__suffix == 'cache'
            assert _.bucket_name()       == 'mgraph-ai-llms-000000000000-cache'
            assert _.bucket_exists()     is True


