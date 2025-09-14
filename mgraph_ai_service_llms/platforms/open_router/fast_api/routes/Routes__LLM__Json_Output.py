from osbot_fast_api.api.routes.Fast_API__Routes                                                         import Fast_API__Routes
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Tag                                              import Safe_Str__Fast_API__Route__Tag
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Json_Extract__Request     import Schema__Json_Extract__Request
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Json_Extract__Response    import Schema__Json_Extract__Response
from mgraph_ai_service_llms.platforms.open_router.service.Service__LLM__Json_Output                     import Service__LLM__Json_Output

TAG__ROUTES_LLM_JSON = Safe_Str__Fast_API__Route__Tag('llm-json')


class Routes__LLM__Json_Output(Fast_API__Routes):
    tag          : Safe_Str__Fast_API__Route__Tag = TAG__ROUTES_LLM_JSON
    service_json : Service__LLM__Json_Output

    def extract(self, json_extract: Schema__Json_Extract__Request) -> Schema__Json_Extract__Response:            # Main extraction endpoint
        with json_extract as _:
            return self.service_json.extract(text_content  = _.text_content ,
                                             output_schema = _.output_schema,
                                             model         = _.model        ,
                                             provider      = _.provider     ,
                                             temperature   = _.temperature  ,
                                             max_tokens    = _.max_tokens   )

    def setup_routes(self):
        self.add_route_post(self.extract)
        return self