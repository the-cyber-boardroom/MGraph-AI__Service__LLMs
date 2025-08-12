from typing                                                         import Dict, Any, Optional
from osbot_utils.helpers.llms.cache.LLM_Request__Cache__File_System import LLM_Request__Cache__File_System
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.utils.Json                                         import json_dumps
from osbot_utils.utils.Misc                                         import str_md5
from mgraph_ai_service_llms.service.cache.LLM__Cache                import LLM__Cache


class LLM__Cache_Manager(Type_Safe):                        # Manages caching of LLM requests and responses"""
    virtual_storage  : LLM__Cache                         = None
    llm_cache        : LLM_Request__Cache__File_System    = None
    cache_enabled    : bool                               = True

    def setup(self):
        if self.cache_enabled:
            self.virtual_storage = LLM__Cache().setup()
            self.llm_cache       = LLM_Request__Cache__File_System(virtual_storage=self.virtual_storage).setup()

    def generate_cache_key(self,
                          model      : str,
                          messages   : list,
                          temperature: float,
                          max_tokens : int) -> str:     # Generate a unique cache key for the request
        cache_data = {  "model"      : model,           # todo: convert to Schema_*
                        "messages"   : messages,
                        "temperature": temperature,
                        "max_tokens" : max_tokens }
        cache_string = json_dumps(cache_data, sort_keys=True)
        return str_md5(cache_string)

    def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:      # Retrieve cached response if it exists
        if not self.cache_enabled or not self.llm_cache:
            return None

        file_path = self.virtual_storage.file_path(cache_key + '.json')         # Use the file system cache to retrieve
        if self.virtual_storage.file__exists(file_path):
            return self.virtual_storage.file_load__json(file_path)


    def cache_response(self, cache_key: str, response: Dict[str, Any]) -> bool: # Cache the response for future use
        if not self.cache_enabled or not self.llm_cache:
            return False

        file_path = self.virtual_storage.file_path(cache_key + '.json')         # Store in virtual storage
        self.virtual_storage.file_save__json(file_path, response)
        return True


    # # todo: see if we need this method, which would be very destructure
    # def clear_cache(self) -> bool:  # Clear all cached responses
    #     if not self.cache_enabled:
    #         return False
    #
    #     for file_path in self.virtual_storage.files():      # Clear all files in the virtual storage
    #         self.virtual_storage.file_delete(file_path)
    #     return True

    # # todo see if we need this method, since this would be quite expensive in a cloud storage with large number of cached files
    # def get_cache_stats(self) -> Dict[str, Any]:
    #     """Get statistics about the cache"""
    #     if not self.cache_enabled or not self.virtual_storage:
    #         return {"enabled": False}
    #
    #     try:
    #         files = self.virtual_storage.files()
    #         total_size = sum(
    #             self.virtual_storage.file_size(f) for f in files
    #         )
    #
    #         return {
    #             "enabled"     : True,
    #             "total_items" : len(files),
    #             "total_size"  : total_size,
    #             "bucket_name" : self.virtual_storage.s3_db.bucket_name(),
    #             "root_folder" : str(self.virtual_storage.root_folder)
    #         }
    #     except Exception as e:
    #         return {
    #             "enabled": True,
    #             "error"  : str(e)
    #         }