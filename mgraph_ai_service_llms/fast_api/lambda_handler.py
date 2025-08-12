import os


if os.getenv('AWS_REGION'):  # only execute if we are running inside an AWS Lambda function

    from osbot_aws.aws.lambda_.boto3__lambda import load_dependencies
    from mgraph_ai_service_llms.config       import LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS

    load_dependencies(LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS)

    def clear_osbot_modules():
        import sys
        for module in list(sys.modules):
            if module.startswith('osbot_aws'):
                del sys.modules[module]

    clear_osbot_modules()

if os.getenv('LOCALSTACK_ENABLED', 'false').lower() == 'true':                      # Check if we should use LocalStack (for local development/testing)
    from mgraph_ai_service_llms.utils.LocalStack__Setup import LocalStack__Setup
    LocalStack__Setup.setup_for_lambda_handler()

from mgraph_ai_service_llms.fast_api.Service__Fast_API import Service__Fast_API

with Service__Fast_API() as _:
    _.setup()
    handler = _.handler()
    app     = _.app()

def run(event, context=None):
    return handler(event, context)