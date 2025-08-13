from osbot_utils.type_safe.Type_Safe                     import Type_Safe
from osbot_utils.utils.Env                               import get_env, set_env
from osbot_local_stack.local_stack.Local_Stack           import Local_Stack
from osbot_aws.testing.Temp__Random__AWS_Credentials     import Temp_AWS_Credentials
from mgraph_ai_service_llms.config                       import LOCALSTACK__ENDPOINT_URL, LOCALSTACK__REGION_NAME, ENV_VAR__LOCALSTACK_ENABLED


class LocalStack__Setup(Type_Safe):         # Helper class to setup LocalStack for development

    local_stack           : Local_Stack           = None
    temp_aws_credentials  : Temp_AWS_Credentials  = None

    def is_localstack_enabled(self) -> bool:                                        # Check if LocalStack is enabled via environment or config
        return get_env(ENV_VAR__LOCALSTACK_ENABLED, "false").lower() == "true"

    def setup(self):                                                                # Setup LocalStack if enabled
        if not self.is_localstack_enabled():
            return self

        self.temp_aws_credentials = Temp_AWS_Credentials     ()                     # Setup temporary AWS credentials for LocalStack
        self.temp_aws_credentials.with_localstack_credentials()

        self.local_stack = Local_Stack()                                            # Initialize and activate LocalStack
        self.local_stack.activate()

        # Set environment variables for AWS SDK
        set_env("AWS_ENDPOINT_URL"  , LOCALSTACK__ENDPOINT_URL)
        set_env("AWS_DEFAULT_REGION", LOCALSTACK__REGION_NAME)

        return self


    # @classmethod
    # def setup_for_lambda_handler(cls): #Static method to setup LocalStack in lambda handler
    #     if get_env(ENV_VAR__LOCALSTACK_ENABLED, "false").lower() == "true":
    #         setup = cls()
    #         setup.setup()
    #         return setup
    #     return None
