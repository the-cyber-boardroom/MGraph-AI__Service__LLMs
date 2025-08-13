from osbot_fast_api.api.Fast_API_Routes                  import Fast_API_Routes
from mgraph_ai_service_llms.service.cache.Service__Cache import Service__Cache

TAG__ROUTES_CACHE = 'cache'
ROUTES_PATHS__CACHE = [ f'/{TAG__ROUTES_CACHE}/index'         ,
                        f'/{TAG__ROUTES_CACHE}/entry-by-id'   ,
                        f'/{TAG__ROUTES_CACHE}/entry-by-hash' ,
                        f'/{TAG__ROUTES_CACHE}/stats'         ]

class Routes__Cache(Fast_API_Routes):
    tag           : str            = 'cache'
    service_cache : Service__Cache = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service_cache = Service__Cache()

    def index(self):                                                        # GET /cache/index
        """Get the complete cache index"""
        return self.service_cache.cache_index()

    def entry_by_id(self, cache_id: str):                                   # GET /cache/entry_by_id?cache_id=xxx
        """Get a cache entry by its cache ID"""
        return self.service_cache.get_cache_entry_by_id(cache_id)

    def entry_by_hash(self, request_hash: str):                             # GET /cache/entry_by_hash?request_hash=xxx
        """Get a cache entry by its request hash"""
        return self.service_cache.get_cache_entry_by_hash(request_hash)

    def stats(self):                                                        # GET /cache/stats
        """Get cache statistics"""
        return self.service_cache.cache_stats()

    def setup_routes(self):
        self.add_route_get(self.index        )
        self.add_route_get(self.entry_by_id  )
        self.add_route_get(self.entry_by_hash)
        self.add_route_get(self.stats        )