from fastapi                                                         import FastAPI
from osbot_fast_api.api.Fast_API                                     import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_utils.helpers.Random_Guid                                 import Random_Guid
from osbot_utils.type_safe.Type_Safe                                 import Type_Safe
from osbot_utils.utils.Env                                           import set_env
from starlette.testclient                                            import TestClient
from mgraph_ai_service_llms.config                                   import ENV_VAR__LOCALSTACK_ENABLED
from mgraph_ai_service_llms.fast_api.Service__Fast_API               import Service__Fast_API
from mgraph_ai_service_llms.utils.LocalStack__Setup                  import LocalStack__Setup

TEST_API_KEY__NAME  = 'key-used-in-pytest'
TEST_API_KEY__VALUE = Random_Guid()

class Service__Fast_API__Test_Objs(Type_Safe):
    fast_api         : Service__Fast_API = None
    fast_api__app    : FastAPI           = None
    fast_api__client : TestClient        = None
    localstack_setup : LocalStack__Setup = None
    setup_completed  : bool              = False

service_fast_api_test_objs = Service__Fast_API__Test_Objs()


def setup__service_fast_api_test_objs():
    """Setup test objects for Service__Fast_API with LocalStack support"""
    with service_fast_api_test_objs as _:
        if _.setup_completed is False:
            set_env(ENV_VAR__LOCALSTACK_ENABLED, 'True')            # make sure it is enabled
            _.localstack_setup = LocalStack__Setup().setup()        # Setup LocalStack

            _.fast_api         = Service__Fast_API().setup()        # Setup Fast API service
            _.fast_api__app    = _.fast_api.app()
            _.fast_api__client = _.fast_api.client()

            # Set API key environment variables for testing
            set_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME , TEST_API_KEY__NAME )
            set_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE, TEST_API_KEY__VALUE)

            _.setup_completed  = True

    return service_fast_api_test_objs


def teardown__service_fast_api_test_objs():
    """Teardown test objects and LocalStack resources"""
    with service_fast_api_test_objs as _:
        if _.setup_completed:
            if _.localstack_setup:
                _.localstack_setup.teardown()
            _.setup_completed = False
    return service_fast_api_test_objs