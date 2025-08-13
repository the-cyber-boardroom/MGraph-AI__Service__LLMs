from typing                                             import Dict, Any
from osbot_utils.helpers.safe_str.Safe_Str__File__Name  import Safe_Str__File__Name
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.type_safe.Type_Safe                    import Type_Safe
from osbot_utils.utils.Http                             import url_join_safe
from mgraph_ai_service_llms.service.cache.LLM__Cache    import LLM__Cache


class Service__Cache(Type_Safe):
    llm_cache          : LLM__Cache           = None
    base_folder        : Safe_Str__File__Path = Safe_Str__File__Path('llm-cache/'     )
    cache_index_path   : Safe_Str__File__Name = Safe_Str__File__Name('cache_index.json')
    _cached_index      : dict                 = None  # In-memory cache of the index

    def __init__(self):
        super().__init__()
        self.llm_cache = LLM__Cache().setup()

    def cache_index(self) -> Dict[str, Any]:                                # Get the complete cache index
        """Return the complete cache index from cache_index.json"""
        try:
            cache_path = url_join_safe(self.base_folder, self.cache_index_path)
            index_content = self.llm_cache.json__load(cache_path)

            if index_content:
                self._cached_index = index_content
                return { 'status': 'success',
                         'data': self._cached_index ,
                         'cache_path': cache_path }
            else:
                return { 'status': 'success',
                         'data'  : { 'cache_id__from__hash__request': {},
                                     'cache_id__to__file_path'      : {},
                                     'message'                      : 'Cache index is empty or not initialized' } }
        except Exception as e:
            return { 'status' : 'error',
                     'message': f'Failed to read cache index: {str(e)}',
                     'data'   : {'cache_path': cache_path}
            }

    def get_cache_entry_by_id(self, cache_id: str) -> Dict[str, Any]:       # Get cache entry by cache ID
        """Retrieve a cache entry by its cache ID"""
        try:
            # Get the file path from the index
            if not self._cached_index:
                self.cache_index()  # Load index if not already loaded

            if not self._cached_index:
                return {
                    'status': 'error',
                    'message': 'Could not load cache index',
                    'cache_id': cache_id,
                    'data': None
                }

            # Look up the file path for this cache ID
            file_path = self._cached_index.get('cache_id__to__file_path', {}).get(cache_id)

            if not file_path:
                return {
                    'status': 'error',
                    'message': f'Cache ID {cache_id} not found in index',
                    'cache_id': cache_id,
                    'data': None
                }

            # Read the actual cache file
            cached_content = self.llm_cache.json__load(file_path)

            if cached_content:
                return {
                    'status'    : 'success',
                    'cache_id'  : cache_id,
                    'file_path' : file_path,
                    'data'      : cached_content
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Cache file not found at path: {file_path}',
                    'cache_id': cache_id,
                    'file_path': file_path,
                    'data': None
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to retrieve cache entry: {str(e)}',
                'cache_id': cache_id,
                'data': None
            }

    def get_cache_entry_by_hash(self, request_hash: str) -> Dict[str, Any]: # Get cache entry by request hash
        """Retrieve a cache entry by its request hash"""
        try:
            # Load index if not already loaded
            if not self._cached_index:
                self.cache_index()

            if not self._cached_index:
                return {
                    'status': 'error',
                    'message': 'Could not load cache index',
                    'request_hash': request_hash,
                    'data': None
                }

            # Get cache ID from the hash
            cache_id = self._cached_index.get('cache_id__from__hash__request', {}).get(request_hash)

            if not cache_id:
                # Try with just the first 10 characters if full hash not found
                short_hash = request_hash[:10] if len(request_hash) >= 10 else request_hash
                cache_id = self._cached_index.get('cache_id__from__hash__request', {}).get(short_hash)

            if not cache_id:
                return {
                    'status': 'error',
                    'message': f'Request hash {request_hash} not found in index',
                    'request_hash': request_hash,
                    'data': None
                }

            # Now get the entry by cache ID
            result = self.get_cache_entry_by_id(cache_id)
            result['request_hash'] = request_hash

            return result

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to retrieve cache entry by hash: {str(e)}',
                'request_hash': request_hash,
                'data': None
            }

    def cache_stats(self) -> Dict[str, Any]:                                # Get cache statistics
        """Get statistics about the cache"""
        try:
            if not self._cached_index:
                self.cache_index()

            if not self._cached_index:
                return {
                    'status': 'error',
                    'message': 'Could not load cache index',
                    'data': None
                }

            hash_to_id = self._cached_index.get('cache_id__from__hash__request', {})
            id_to_path = self._cached_index.get('cache_id__to__file_path', {})

            # Extract model usage from file paths
            models_count = {}
            dates_count = {}

            for cache_id, file_path in id_to_path.items():
                # Parse model from path: "model_name/2025/07/23/15/cache_id.json"
                parts = file_path.split('/')
                if len(parts) > 0:
                    model = parts[0].replace('_', '/')  # Convert back underscores to slashes
                    models_count[model] = models_count.get(model, 0) + 1

                # Parse date from path
                if len(parts) >= 4:
                    date = f"{parts[1]}/{parts[2]}/{parts[3]}"  # YYYY/MM/DD
                    dates_count[date] = dates_count.get(date, 0) + 1

            stats = {
                'total_entries': len(id_to_path),
                'total_request_hashes': len(hash_to_id),
                'models_distribution': models_count,
                'dates_distribution': dates_count,
                'bucket_name': self.llm_cache.s3_db.bucket_name() if self.llm_cache.s3_db else 'unknown',
                'root_folder': str(self.llm_cache.root_folder)
            }

            return {
                'status': 'success',
                'data': stats
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to calculate cache stats: {str(e)}',
                'data': None
            }