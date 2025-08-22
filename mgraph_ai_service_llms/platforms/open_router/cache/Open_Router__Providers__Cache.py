from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id               import Safe_Id
from memory_fs.file_fs.File_FS                                                   import File_FS
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now                     import Timestamp_Now
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache       import Open_Router__Cache

FILE_ID__OPEN_ROUTER__PROVIDERS = "openrouter-providers"

class Open_Router__Providers__Cache(Type_Safe):
    cache           : Open_Router__Cache = None                                  # Cache backend
    cache_ttl_hours : int                = 24                                    # Providers change less frequently

    def setup(self) -> 'Open_Router__Providers__Cache':                          # Initialize cache system
        if self.cache is None:
            self.cache = Open_Router__Cache()
            self.cache.s3__prefix = "providers"                                  # Use different prefix for providers # todo: see if this should not be the same for all openrouter api data
            self.cache.setup()
        return self

    def cache_providers_response(self, providers_data: dict                      # Cache complete providers response
                                 ) -> File_FS:
        cache_metadata = {}                                                      # Create cache metadata
        cache_metadata['cache_timestamp'] = Timestamp_Now()
        cache_metadata['cache_ttl_hours'] = self.cache_ttl_hours

        with self.cache.fs__latest_temporal.file__json(FILE_ID__OPEN_ROUTER__PROVIDERS) as _:
            _.create          (providers_data )
            _.metadata__update(cache_metadata )
            return _

    def get_cached_providers(self) -> dict:                                      # Retrieve cached providers data
        with self.cache.fs__latest_temporal.file__json(FILE_ID__OPEN_ROUTER__PROVIDERS) as _:
            if _.exists():
                return _.content()
            return None

    def is_cache_valid(self) -> bool:                                            # Check if cache is valid based on TTL
        with self.cache.fs__latest_temporal.file__json(FILE_ID__OPEN_ROUTER__PROVIDERS) as _:
            if not _.exists():
                return False

            metadata = _.metadata()
            if not metadata or not metadata.data:
                return False

            cache_timestamp = metadata.data.get(Safe_Id('cache_timestamp'))
            if not cache_timestamp:
                return False

            # Check age
            current_time = Timestamp_Now()
            age_hours = (current_time - cache_timestamp) / 3600
            ttl_hours = metadata.data.get(Safe_Id('cache_ttl_hours'), self.cache_ttl_hours)

            return age_hours < ttl_hours

    # def get_providers_with_fallback(self, fetch_function                         # Get providers with cache fallback
    #                                 ) -> dict:
    #     if self.is_cache_valid():                                               # Check cache validity
    #         cached_data = self.get_cached_providers()
    #         if cached_data:
    #             return cached_data
    #
    #     # Fetch fresh data
    #     try:
    #         fresh_data = fetch_function()
    #         # Cache the fresh data
    #         self.cache_providers_response(fresh_data)
    #         return fresh_data
    #     except Exception as e:
    #         # Fallback to stale cache if fetch fails
    #         cached_data = self.get_cached_providers()
    #         if cached_data:
    #             return cached_data
    #         raise

    # def cache_provider_status(self, provider_id: str,                            # Cache individual provider status
    #                                 status_data: dict
    #                           ) -> File_FS:
    #     status_metadata = {}
    #     status_metadata['cache_timestamp'] = Timestamp_Now()
    #     status_metadata['cache_ttl_hours'] = 1                                   # Status updates more frequently
    #
    #     file_id = f"provider-status-{provider_id}"
    #     with self.cache.fs__latest_temporal.file__json(file_id) as _:
    #         _.update          (status_data    )
    #         _.metadata__update(status_metadata)
    #         return _
    #
    # def get_provider_status(self, provider_id: str                               # Get cached provider status
    #                         ) -> dict:
    #     file_id = f"provider-status-{provider_id}"
    #     with self.cache.fs__latest_temporal.file__json(file_id) as _:
    #         if _.exists():
    #             return _.content()
    #         return None
    #
    # def clear_provider_cache(self) -> bool:                                      # Clear all provider cache
    #     return self.cache.clear_all()