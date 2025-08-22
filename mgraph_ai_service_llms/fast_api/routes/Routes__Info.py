from osbot_fast_api.api.routes.Fast_API__Routes        import Fast_API__Routes
from mgraph_ai_service_llms.service.info.Service_Info  import Service_Info

TAG__ROUTES_INFO                  = 'info'
ROUTES_PATHS__INFO                = [ f'/{TAG__ROUTES_INFO}/health'  ,
                                      f'/{TAG__ROUTES_INFO}/server'  ,
                                      f'/{TAG__ROUTES_INFO}/status'  ,
                                      f'/{TAG__ROUTES_INFO}/versions']
ROUTES_INFO__HEALTH__RETURN_VALUE = {'status': 'ok'}

class Routes__Info(Fast_API__Routes):
    tag         : str          = 'info'
    service_info: Service_Info

    def health(self):
        return ROUTES_INFO__HEALTH__RETURN_VALUE

    def server(self):                                             # Get service versions
        return self.service_info.server_info()

    def status(self):                                               # Get service status information
        return self.service_info.service_info()

    def versions(self):                                             # Get service versions
        return self.service_info.versions()


    def setup_routes(self):
        self.add_route_get(self.health  )
        self.add_route_get(self.server  )
        self.add_route_get(self.status  )
        self.add_route_get(self.versions)