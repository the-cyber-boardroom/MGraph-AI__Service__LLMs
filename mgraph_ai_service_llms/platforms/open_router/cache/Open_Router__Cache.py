from typing                                                         import Any, Type
from memory_fs.file_fs.File_FS                                      import File_FS
from memory_fs.helpers.Memory_FS__Latest                            import Memory_FS__Latest
from memory_fs.helpers.Memory_FS__Latest_Temporal                   import Memory_FS__Latest_Temporal
from memory_fs.helpers.Memory_FS__Temporal                          import Memory_FS__Temporal
from memory_fs.schemas.Schema__Memory_FS__File__Type                import Schema__Memory_FS__File__Type
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id  import Safe_Id
from mgraph_ai_service_llms.service.s3.Storage_FS__S3               import Storage_FS__S3

class Open_Router__Cache(Type_Safe):
    s3__bucket          : str                         = "openrouter-cache"                                 # S3 bucket for cache storage
    s3__prefix          : str                         = "models"                                           # Prefix for all cache entries
    s3__storage         : Storage_FS__S3              = None                                               # S3 storage backend
    fs__latest          : Memory_FS__Latest           = None
    fs__temporal        : Memory_FS__Temporal         = None
    fs__latest_temporal : Memory_FS__Latest_Temporal  = None                                               # Memory-FS with latest+temporal
    
    def setup(self) -> 'Open_Router__Cache':                                                                    # Initialize cache system
        self.s3__storage         = Storage_FS__S3            ( s3_bucket   = self.s3__bucket,                   # Setup S3 storage
                                                               s3_prefix   = self.s3__prefix).setup()           # with prefix 'models'
        self.fs__temporal        = Memory_FS__Temporal       ( storage_fs  = self.s3__storage)                  # Create Memory_FS with latest+temporal pattern
        self.fs__latest_temporal = Memory_FS__Latest_Temporal( storage_fs  = self.s3__storage)                  # Create Memory_FS with latest+temporal pattern
        self.fs__latest          = Memory_FS__Latest         ( storage_fs  = self.s3__storage)                  # Create a Memory_FS with just latest handler

        return self

    
    def file_for_latest(self, file_id   : Safe_Id                                    ,                           # Create file for latest cache
                              file_type : Type[Schema__Memory_FS__File__Type] = None
                        ) -> File_FS:
        return self.fs__latest.file(file_id=file_id, file_type=file_type)

    def file_for_temporal(self, file_id  : Safe_Id                                     ,                         # Create file for temporal cache
                                file_type : Type[Schema__Memory_FS__File__Type] = None
                          ) -> Any:
        return self.fs__temporal.file(file_id=file_id, file_type=file_type)

    def file_for_latest_temporal(self, file_id   : Safe_Id                                    ,                           # Create file for latest cache
                                       file_type : Type[Schema__Memory_FS__File__Type] = None
                                  ) -> File_FS:
        return self.fs__latest_temporal.file(file_id=file_id, file_type=file_type)
    
    def clear_all(self) -> bool:                                                        # Clear all cache entries
        return self.s3__storage.clear()
