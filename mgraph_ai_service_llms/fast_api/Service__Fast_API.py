import logging

from osbot_fast_api.api.routes.Routes__Config                                    import Routes__Config
from osbot_fast_api.api.routes.Routes__Set_Cookie                                import Routes__Set_Cookie
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API                     import Serverless__Fast_API
from osbot_utils.utils.Files import path_combine
from starlette.staticfiles import StaticFiles

import mgraph_ai_service_llms
from mgraph_ai_service_llms.config                                               import FAST_API__TITLE
from mgraph_ai_service_llms.fast_api.routes.Routes__Cache                        import Routes__Cache
from mgraph_ai_service_llms.fast_api.routes.Routes__Info                         import Routes__Info
from mgraph_ai_service_llms.fast_api.routes.Routes__LLMs                         import Routes__LLMs
from mgraph_ai_service_llms.platforms.open_router.fast_api.Open_Router__Fast_API import Open_Router__Fast_API
from mgraph_ai_service_llms.utils.LocalStack__Setup                              import LocalStack__Setup
from mgraph_ai_service_llms.utils.Version                                        import version__mgraph_ai_service_llms



class Service__Fast_API(Serverless__Fast_API):
    add_admin_ui : bool = True

    def fast_api__title(self):                                       # todo: move this to the Fast_API class
        return FAST_API__TITLE

    def setup(self):
        self.setup_localstack()
        super().setup()
        self.setup_fast_api_title_and_version()                     # todo: add this support to the Fast_API class
        return self

    def setup_fast_api_title_and_version(self):                     # todo: move this to the Fast_API class
        app       = self.app()
        app.title = self.fast_api__title()
        app.version = version__mgraph_ai_service_llms
        return self

    def setup_localstack(self):
        with LocalStack__Setup() as _:
            if _.is_localstack_enabled():
                logger = logging.getLogger("uvicorn")       # todo: add this logging support to Fast_API
                logger.warning('LocalStack enabled')
                _.setup()

    def path_static_folder(self):
        return path_combine(mgraph_ai_service_llms.path, 'web-mvps')

    def setup_static_routes(self):
        path_static_folder = self.path_static_folder()
        if path_static_folder:
            path_name   = "web-mvps"
            path_static = f"/{path_name}"
            self.app().mount(path_static                                         ,
                             StaticFiles(directory=path_static_folder, html=True),
                             name=path_name                                      )

    def setup_routes(self):
        self.add_routes    (Routes__Info         )
        self.add_routes    (Routes__Config       )
        self.add_routes    (Routes__Set_Cookie   )
        self.add_routes    (Routes__LLMs         )
        self.add_routes    (Routes__Cache        )
        self.mount_fast_api(Open_Router__Fast_API)



