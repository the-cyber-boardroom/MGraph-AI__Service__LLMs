from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now                        import Timestamp_Now
from osbot_utils.type_safe.primitives.safe_str.cryptography.hashes.Safe_Str__Hash   import Safe_Str__Hash, SIZE__VALUE_HASH
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                  import Safe_Id
from osbot_utils.utils.Json                                                         import json_to_str
from osbot_utils.utils.Misc                                                         import bytes_sha256
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache          import Open_Router__Cache

class Open_Router__Chat__Cache(Type_Safe):
    cache: Open_Router__Cache = None
    cache_ttl_hours: int = 24                                                       # Chat responses are cached for 24h

    def setup(self) -> 'Open_Router__Chat__Cache':
        if self.cache is None:
            self.cache = Open_Router__Cache()
            self.cache.s3__prefix = "chat"  # Different prefix for chat cache
            self.cache.setup()
        return self

    def generate_cache_id(self, request_data: dict) -> Safe_Str__Hash:                      # Generate deterministic cache ID from request parameters
        cache_key= json_to_str(request_data)                                                # use the entire request as the cache key
        hash_value = bytes_sha256(cache_key.encode())[:SIZE__VALUE_HASH]                    # First 10 chars of hash
        return Safe_Str__Hash(hash_value)
        return Safe_Id(f"chat_{hash_value}")

    def cache_chat_response(self, request_data: dict, response_data: dict) -> bool:         # Cache a chat completion response"""
        cache_id = self.generate_cache_id(request_data)

        cache_entry = { 'request'   : request_data         ,
                        'response'  : response_data        ,
                        'cached_at' : Timestamp_Now()      ,
                        'ttl_hours' : self.cache_ttl_hours }
        file_id = Safe_Id(cache_id)                                                         # we need to convert Safe_Str__Hash into Safe_ID
        with self.cache.fs__latest_temporal.file__json(file_id) as _:
            _.create(cache_entry)
            return True

    def get_cached_response(self, request_data: dict) -> dict:          # Retrieve cached response if available and valid
        cache_id = self.generate_cache_id(request_data)
        file_id  = Safe_Id(cache_id)
        with self.cache.fs__latest_temporal.file__json(file_id) as _:
            if _.exists():
                cache_entry = _.content()

                cached_at = cache_entry.get('cached_at', 0)                 # Check TTL
                current_time = Timestamp_Now()
                age_hours    = (current_time - cached_at) / 3_600_000
                print('------')
                print(age_hours)

                if age_hours < self.cache_ttl_hours:
                    return cache_entry.get('response')

        return None