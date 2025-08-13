from unittest                                    import TestCase
from tests.deploy_aws.test_Deploy__Service__base import test_Deploy__Service__base

class test_Deploy__Service__to__dev(test_Deploy__Service__base, TestCase):
    stage = 'dev'

    # def request_payload(self, path='/'):
    #     payload = {'version': '2.0',
    #                'requestContext': {'http': {'method': 'GET',
    #                                            'path': path,
    #                                            'sourceIp': '127.0.0.1'}}}
    #     return payload
    #
    # def test_4__invoke__get_logs(self):
    #     #self.test_2__upload_dependencies()
    #     #self.test_3__create()
    #     from osbot_utils.utils.Dev import pprint
    #     payload  = self.request_payload()
    #     response = self.deploy_fast_api.lambda_function().invoke_return_logs(payload)
    #     pprint(response)
    #     #response = self.deploy_fast_api.lambda_function().invoke(payload)
    #     #pprint(response)
    #
    #     pprint(self.deploy_fast_api.lambda_function().function_url())
