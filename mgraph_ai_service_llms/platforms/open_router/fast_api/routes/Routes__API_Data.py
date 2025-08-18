from osbot_fast_api.api.routes.Fast_API__Routes                               import Fast_API__Routes
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Tag                    import Safe_Str__Fast_API__Route__Tag
from mgraph_ai_service_llms.platforms.open_router.Service__Open_Router__Models import Service__Open_Router__Models


class Routes__API_Data(Fast_API__Routes):
    tag        : Safe_Str__Fast_API__Route__Tag = 'api/data'
    open_router: Service__Open_Router__Models

    def v1_models_raw(self):
        return self.open_router.get_cached_models()

    def setup_routes(self):
        self.add_route_get(self.v1_models_raw)