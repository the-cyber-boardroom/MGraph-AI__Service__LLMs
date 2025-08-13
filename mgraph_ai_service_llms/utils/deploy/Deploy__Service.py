from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API                  import Deploy__Serverless__Fast_API
from osbot_utils.utils.Env                                                          import get_env
from mgraph_ai_service_llms.config                                                  import SERVICE_NAME, LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS
from mgraph_ai_service_llms.fast_api.lambda_handler                                 import run
from mgraph_ai_service_llms.service.llms.providers.open_router.Provider__OpenRouter import ENV_NAME_OPEN_ROUTER__API_KEY


class Deploy__Service(Deploy__Serverless__Fast_API):

    def deploy_lambda(self):
        with super().deploy_lambda() as _:
            # Add any service-specific environment variables here
            _.set_env_variable(ENV_NAME_OPEN_ROUTER__API_KEY, get_env(ENV_NAME_OPEN_ROUTER__API_KEY))
            return _

    def handler(self):
        return run

    def lambda_dependencies(self):
        return LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS

    def lambda_name(self):
        return SERVICE_NAME