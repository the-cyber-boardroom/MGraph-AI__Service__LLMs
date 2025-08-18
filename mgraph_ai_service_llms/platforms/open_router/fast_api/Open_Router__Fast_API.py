from osbot_fast_api.api.Fast_API            import Fast_API

from mgraph_ai_service_llms.platforms.open_router.fast_api.routes.Routes__API_Data import Routes__API_Data
from mgraph_ai_service_llms.utils.Version   import version__mgraph_ai_service_llms

FAST_API__TITLE__OPEN_ROUTER = 'Platform - Open Router'

class Open_Router__Fast_API(Fast_API):
    base_path      = '/platform/open-router'
    default_routes = False

    def setup(self):
        super().setup()
        self.setup_fast_api_title_and_version()
        return self

    def setup_fast_api_title_and_version(self):
        app       = self.app()
        app.title = FAST_API__TITLE__OPEN_ROUTER
        app.version = version__mgraph_ai_service_llms
        return self

    def setup_routes(self):
        self.add_routes(Routes__API_Data)