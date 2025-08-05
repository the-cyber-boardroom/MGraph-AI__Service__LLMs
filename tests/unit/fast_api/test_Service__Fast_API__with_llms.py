from unittest                                                import TestCase
from fastapi                                                 import FastAPI
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API import Serverless__Fast_API
from osbot_utils.type_safe.Type_Safe                        import Type_Safe
from osbot_utils.utils.Objects                              import base_classes
from mgraph_ai_service_llms.fast_api.Service__Fast_API      import Service__Fast_API
from tests.unit.Service__Fast_API__Test_Objs                import setup__service_fast_api_test_objs


class test_Service__Fast_API__with_llms(TestCase):

    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.service_fast_api_test_objs = _
            cls.fast_api                   = _.fast_api
            cls.fast_api__app              = _.fast_api__app
            cls.fast_api__client           = _.fast_api__client

    def test__init__(self):
        with self.fast_api as _:
            assert type(_)         == Service__Fast_API
            assert base_classes(_) == [Serverless__Fast_API, Fast_API, Type_Safe, object]
            assert type(_.app())   == FastAPI

    def test__routes_include_llms(self):
        routes = self.fast_api.routes_paths()

        # Check LLM routes are included
        assert '/llms/complete' in routes
        assert '/llms/models'   in routes

        # Check other routes still exist
        assert '/info/health'   in routes
        assert '/info/server'   in routes
        assert '/info/status'   in routes
        assert '/info/versions' in routes

        # Verify total route count increased
        assert len(routes) >= 6  # At least info routes + llm routes

    def test__app_configuration(self):
        app = self.fast_api__app

        # Check app is configured correctly
        assert app.title   == "MGraph-AI LLM Service"
        assert app.version == self.fast_api.app().version

        # Check routes are registered
        route_paths = [route.path for route in app.routes]
        assert '/llms/models'   in route_paths
        assert '/llms/complete' in route_paths