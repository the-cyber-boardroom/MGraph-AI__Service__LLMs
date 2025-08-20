# mgraph_ai_service_llms/platforms/open_router/cache/Open_Router__Providers__Cache.py

import logging
from datetime                                                                    import datetime, timedelta
from typing                                                                      import Optional, Dict, Any, List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id               import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path   import Safe_Str__File__Path
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache       import Open_Router__Cache

logger = logging.getLogger(__name__)


class Open_Router__Providers__Cache(Type_Safe):
    cache           : Open_Router__Cache = None                                         # Cache backend
    cache_ttl_hours : int                = 24                                           # Providers change less frequently

    def setup(self) -> 'Open_Router__Providers__Cache':                                 # Initialize cache system
        self.cache = Open_Router__Cache()
        self.cache.s3_prefix = "providers"                                              # Use different prefix for providers
        self.cache.setup()
        return self

    def cache_providers_response(self, providers_data: Dict[str, Any]                   # Cache providers data
                                 ) -> bool:
        timestamp = datetime.now()

        # Add cache metadata
        providers_data['_cache_timestamp'] = timestamp.isoformat()
        providers_data['_cache_ttl_hours'] = self.cache_ttl_hours

        # Save to both latest and temporal
        return self.cache.save_to_both(file_id   = "openrouter-providers",
                                       data      = providers_data         ,
                                       timestamp = timestamp              )

    def get_cached_providers(self) -> Optional[Dict[str, Any]]:                         # Retrieve cached providers
        cached_data = self.cache.load_from_latest("openrouter-providers")

        if cached_data and '_cache_timestamp' not in cached_data:
            metadata = self.cache.get_latest_metadata("openrouter-providers")
            if metadata and 'timestamp' in metadata:
                cached_data['_cache_timestamp'] = metadata.get('timestamp')

        return cached_data

    def is_cache_valid(self, cached_data: Optional[Dict[str, Any]]                      # Check cache validity
                       ) -> bool:
        if not cached_data:
            return False

        cache_timestamp_str = cached_data.get('_cache_timestamp')
        if not cache_timestamp_str:
            return False

        try:
            cache_timestamp = datetime.fromisoformat(cache_timestamp_str)
            age_hours       = (datetime.now() - cache_timestamp).total_seconds() / 3600
            ttl_hours       = cached_data.get('_cache_ttl_hours', self.cache_ttl_hours)

            return age_hours < ttl_hours
        except (ValueError, TypeError):
            return False

    def get_providers_with_fallback(self, fetch_function                                # Get providers with cache fallback
                                    ) -> Dict[str, Any]:
        # Try cache first
        cached_data = self.get_cached_providers()

        if cached_data and self.is_cache_valid(cached_data):
            logger.info("Using valid cached providers data")
            return cached_data

        # Fetch fresh data
        try:
            logger.info("Fetching fresh providers data from API")
            fresh_data = fetch_function()

            # Cache the fresh data
            self.cache_providers_response(fresh_data)

            return fresh_data

        except Exception as e:
            logger.warning(f"Failed to fetch fresh providers: {e}")

            # Fallback to stale cache
            if cached_data:
                logger.warning("Using stale providers cache due to API error")
                return cached_data

            raise

    def get_provider_history(self, days_back: int = 30                                  # Get provider changes history
                             ) -> List[Dict[str, Any]]:
        history = []

        entries = self.cache.list_temporal_entries(file_id_prefix = "openrouter-providers",
                                                   days_back      = days_back             )

        for entry_path in entries:
            try:
                file_path = Safe_Str__File__Path(entry_path)
                data      = self.cache.storage_fs.file__json(file_path)

                if data:
                    history.append({
                        'timestamp' : data.get('_cache_timestamp', entry_path),
                        'providers' : data
                    })
            except Exception as e:
                logger.error(f"Failed to load provider history entry {entry_path}: {e}")
                continue

        return history

    def cache_provider_status(self, provider_id : str           ,                       # Cache individual provider status
                                    status_data : Dict[str, Any]
                              ) -> bool:
        timestamp = datetime.now()

        status_data['_cache_timestamp'] = timestamp.isoformat()
        status_data['_cache_ttl_hours'] = 1                                             # Status updates more frequently

        # Use Memory_FS__Latest for provider status
        from memory_fs.Memory_FS__Latest import Memory_FS__Latest

        status_fs = Memory_FS__Latest(storage_fs = self.cache.storage_fs)
        handler   = status_fs.path_handlers[0]
        handler.prefix_path = Safe_Str__File__Path(f"cache/providers/status")

        file_fs = status_fs.file__json(Safe_Id(provider_id))
        file_fs.create()

        return file_fs.save(status_data)

    def get_provider_status(self, provider_id: str                                      # Get cached provider status
                            ) -> Optional[Dict[str, Any]]:
        from memory_fs.Memory_FS__Latest import Memory_FS__Latest

        status_fs = Memory_FS__Latest(storage_fs = self.cache.storage_fs)
        handler   = status_fs.path_handlers[0]
        handler.prefix_path = Safe_Str__File__Path(f"cache/providers/status")

        file_fs = status_fs.file__json(Safe_Id(provider_id))

        if file_fs.exists():
            return file_fs.content()

        return None

    def clear_provider_cache(self) -> bool:                                             # Clear all provider cache
        logger.info("Clearing all providers cache")
        return self.cache.clear_all()

    def cleanup_old_provider_cache(self, days_to_keep: int = 60                         # Clean up old provider data
                                   ) -> int:
        logger.info(f"Cleaning up provider cache older than {days_to_keep} days")
        return self.cache.clear_old_temporal(days_to_keep)