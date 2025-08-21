from memory_fs.file_fs.File_FS                                                                           import File_FS
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now                                             import Timestamp_Now
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache                               import Open_Router__Cache
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Models__Response   import Schema__Open_Router__Models__Response

FILE_ID__OPEN_ROUTER__MODELS = "openrouter-models"

class Open_Router__Models__Cache(Type_Safe):
    cache           : Open_Router__Cache     = None                                     # Cache backend
    cache_ttl_hours : int                    = 6                                        # Cache TTL in hours

    def setup(self) -> 'Open_Router__Models__Cache':                                    # Initialize cache system
        if self.cache is None:
            self.cache = Open_Router__Cache().setup()
        return self

    def cache_models_response(self, models_response: Schema__Open_Router__Models__Response  # Cache complete models response
                              ) -> File_FS:

        models_data = models_response.json()                        # get models_response json data
        cache_metadata = {}                                         # create cache metadata  # todo: improve this metadata section
        cache_metadata['cache_timestamp'] = Timestamp_Now()
        cache_metadata['cache_ttl_hours'] = self.cache_ttl_hours
        with self.cache.fs__latest_temporal.file__json(FILE_ID__OPEN_ROUTER__MODELS) as _:
            _.create          (models_data   )
            _.metadata__update(cache_metadata)
            return _


    def get_cached_models(self) -> Schema__Open_Router__Models__Response:                            # Retrieve cached models data
        with self.cache.fs__latest_temporal.file__json(FILE_ID__OPEN_ROUTER__MODELS) as _:
            json_data = _.content()
            return Schema__Open_Router__Models__Response.from_json(json_data)