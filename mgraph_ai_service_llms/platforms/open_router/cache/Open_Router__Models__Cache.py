import logging
from datetime                                                                                            import datetime, timedelta
from typing                                                                                              import Optional, List, Dict, Any
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                                       import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path                           import Safe_Str__File__Path
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache                               import Open_Router__Cache
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model              import Schema__Open_Router__Model
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Models__Response   import Schema__Open_Router__Models__Response

logger = logging.getLogger(__name__)


class Open_Router__Models__Cache(Type_Safe):
    cache           : Open_Router__Cache     = None                                     # Cache backend
    cache_ttl_hours : int                    = 6                                        # Cache TTL in hours

    def setup(self) -> 'Open_Router__Models__Cache':                                    # Initialize cache system
        self.cache = Open_Router__Cache().setup()
        return self

    def cache_models_response(self, models_response: Schema__Open_Router__Models__Response  # Cache complete models response
                              ) -> bool:
        timestamp = datetime.now()

        # Convert to JSON-serializable format
        models_data = models_response.json()

        # Add cache metadata
        models_data['_cache_timestamp'] = timestamp.isoformat()
        models_data['_cache_ttl_hours'] = self.cache_ttl_hours

        # Save to both latest and temporal using the combined approach
        success = self.cache.save_to_both(file_id   = "openrouter-models",
                                          data      = models_data         ,
                                          timestamp = timestamp           )

        # Cache individual models
        if success:
            for model in models_response.data:
                self._cache_individual_model(model, timestamp)

        return success

    def _cache_individual_model(self, model    : Schema__Open_Router__Model ,            # Cache individual model data
                                      timestamp : datetime
                                ) -> bool:
        # Create safe filename from model ID
        safe_model_id = str(model.id).replace('/', '_').replace(':', '_')

        model_data = model.json()
        model_data['_cache_timestamp'] = timestamp.isoformat()

        # Use a custom path for individual models
        from memory_fs.Memory_FS__Latest import Memory_FS__Latest

        individual_fs = Memory_FS__Latest(storage_fs = self.cache.storage_fs)

        # Configure path for individual models
        handler = individual_fs.path_handlers[0]
        handler.prefix_path = Safe_Str__File__Path(f"cache/models/individual/{model.canonical_slug}")

        file_fs = individual_fs.file__json(Safe_Id(safe_model_id))
        file_fs.create()

        return file_fs.save(model_data)

    def get_cached_models(self) -> Optional[Dict[str, Any]]:                            # Retrieve cached models data
        cached_data = self.cache.load_from_latest("openrouter-models")

        if cached_data:
            # Add metadata from file if not present
            if '_cache_timestamp' not in cached_data:
                metadata = self.cache.get_latest_metadata("openrouter-models")
                if metadata and 'timestamp' in metadata:
                    cached_data['_cache_timestamp'] = metadata.get('timestamp')

        return cached_data

    def get_cached_model_by_id(self, model_id: str                                      # Get specific cached model
                                ) -> Optional[Dict[str, Any]]:
        # Try to load from individual cache first
        safe_model_id = model_id.replace('/', '_').replace(':', '_')

        # Create Memory_FS for individual model path
        from memory_fs.Memory_FS__Latest import Memory_FS__Latest

        individual_fs = Memory_FS__Latest(storage_fs = self.cache.storage_fs)

        # Try different paths where the model might be cached
        for path_suffix in [safe_model_id, model_id.split('/')[-1]]:
            handler = individual_fs.path_handlers[0]
            handler.prefix_path = Safe_Str__File__Path(f"cache/models/individual")

            file_fs = individual_fs.file__json(Safe_Id(safe_model_id))

            if file_fs.exists():
                return file_fs.content()

        # Fallback to searching in complete models cache
        models_data = self.get_cached_models()
        if models_data and 'data' in models_data:
            for model in models_data['data']:
                if model.get('id') == model_id:
                    return model

        return None

    def is_cache_valid(self, cached_data : Optional[Dict[str, Any]]                     # Check if cache is still valid
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

    def get_models_with_fallback(self, fetch_function                                   # Get models with cache fallback
                                  ) -> List[Schema__Open_Router__Model]:
        # Try cache first
        cached_data = self.get_cached_models()

        if cached_data and self.is_cache_valid(cached_data):
            logger.info("Using valid cached models data")
            return self._parse_cached_models(cached_data)

        # Fetch fresh data
        try:
            logger.info("Fetching fresh models data from API")
            fresh_response = fetch_function()

            # Cache the fresh data
            self.cache_models_response(fresh_response)

            return fresh_response.data

        except Exception as e:
            logger.warning(f"Failed to fetch fresh models: {e}")

            # Fallback to stale cache if available
            if cached_data:
                logger.warning("Using stale cache due to API error")
                return self._parse_cached_models(cached_data)

            raise

    def _parse_cached_models(self, cached_data: Dict[str, Any]                          # Parse cached data to model objects
                             ) -> List[Schema__Open_Router__Model]:
        models = []

        if 'data' in cached_data:
            for model_data in cached_data['data']:
                try:
                    model = Schema__Open_Router__Model.from_json(model_data)
                    models.append(model)
                except Exception as e:
                    logger.error(f"Failed to parse cached model: {e}")
                    continue

        return models

    def get_model_history(self, model_id : str           ,                              # Get historical data for a model
                                days_back : int = 7
                          ) -> List[Dict[str, Any]]:
        history = []

        # Get temporal entries
        entries = self.cache.list_temporal_entries(file_id_prefix = "openrouter-models",
                                                   days_back      = days_back           )

        for entry_path in entries:
            try:
                # Load the temporal entry
                file_path = Safe_Str__File__Path(entry_path)
                data      = self.cache.storage_fs.file__json(file_path)

                if data and 'data' in data:
                    # Find the specific model
                    for model_data in data['data']:
                        if model_data.get('id') == model_id:
                            history.append({
                                'timestamp'  : data.get('_cache_timestamp', entry_path),
                                'model_data' : model_data
                            })
                            break
            except Exception as e:
                logger.error(f"Failed to load history entry {entry_path}: {e}")
                continue

        return history

    def detect_pricing_changes(self) -> List[Dict[str, Any]]:                           # Detect models with pricing changes
        changes = []

        # Get latest models
        latest_data = self.get_cached_models()
        if not latest_data or 'data' not in latest_data:
            return changes

        # Get previous day's data
        yesterday = datetime.now() - timedelta(days=1)
        entries   = self.cache.list_temporal_entries(file_id_prefix = "openrouter-models",
                                                     days_back      = 2                   )

        previous_data = None
        for entry_path in sorted(entries, reverse=True):
            if str(yesterday.date()) in entry_path:
                try:
                    file_path     = Safe_Str__File__Path(entry_path)
                    previous_data = self.cache.storage_fs.file__json(file_path)
                    break
                except Exception:
                    continue

        if not previous_data or 'data' not in previous_data:
            return changes

        # Compare pricing
        latest_models   = {m['id']: m for m in latest_data['data']}
        previous_models = {m['id']: m for m in previous_data['data']}

        for model_id, latest_model in latest_models.items():
            if model_id in previous_models:
                prev_model     = previous_models[model_id]
                latest_pricing = latest_model.get('pricing', {})
                prev_pricing   = prev_model.get('pricing', {})

                if latest_pricing != prev_pricing:
                    changes.append({
                        'model_id' : model_id     ,
                        'name'     : latest_model.get('name', model_id),
                        'previous' : prev_pricing ,
                        'current'  : latest_pricing,
                        'timestamp': datetime.now().isoformat()
                    })

        return changes

    def warm_cache(self, fetch_function                                                 # Pre-populate cache
                   ) -> bool:
        try:
            logger.info("Warming models cache")
            models_response = fetch_function()
            return self.cache_models_response(models_response)
        except Exception as e:
            logger.error(f"Failed to warm cache: {e}")
            return False

    def clear_cache(self) -> bool:                                                      # Clear all cache entries
        logger.info("Clearing all models cache")
        return self.cache.clear_all()

    def cleanup_old_cache(self, days_to_keep: int = 30                                  # Clean up old temporal entries
                          ) -> int:
        logger.info(f"Cleaning up cache older than {days_to_keep} days")
        return self.cache.clear_old_temporal(days_to_keep)