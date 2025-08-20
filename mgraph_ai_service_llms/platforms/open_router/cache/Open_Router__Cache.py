from datetime                                                                    import datetime
from typing import Optional, Dict, Any, Type

from memory_fs.file_fs.File_FS import File_FS
from memory_fs.helpers.Memory_FS__Latest                                         import Memory_FS__Latest
from memory_fs.helpers.Memory_FS__Latest_Temporal                                import Memory_FS__Latest_Temporal
from memory_fs.helpers.Memory_FS__Temporal                                       import Memory_FS__Temporal
from memory_fs.schemas.Schema__Memory_FS__File__Type import Schema__Memory_FS__File__Type
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id               import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path   import Safe_Str__File__Path
from mgraph_ai_service_llms.service.s3.Storage_FS__S3                            import Storage_FS__S3

#PREFIX_PATH__OPEN_ROUTER__CACHE = "cache"

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
        
        return latest_fs.file__json(file_id)
    
    def file_for_temporal(self, file_id  : Safe_Id                                     ,                         # Create file for temporal cache
                                file_type : Type[Schema__Memory_FS__File__Type] = None ,
                                timestamp : Optional[datetime] = None
                          ) -> Any:
        return self.fs__temporal.file(file_id=file_id, file_type=file_type)
        if timestamp is None:
            timestamp = datetime.now()
        
        # Create unique file ID with timestamp
        temporal_file_id = Safe_Id(f"{file_id}-{timestamp.isoformat()}")
        
        # Create a Memory_FS with just temporal handler
        temporal_fs = Memory_FS__Temporal(storage_fs = self.storage_fs)
        temporal_fs.path_handlers[0].prefix_path = Safe_Str__File__Path("cache")
        
        return temporal_fs.file__json(temporal_file_id)
    
    def save_to_latest(self, file_id : str ,                                            # Save data to latest cache
                             data     : dict
                       ) -> bool:
        file_fs = self.file_for_latest(Safe_Id(file_id))
        file_fs.create()
        return file_fs.save(data)
    
    def save_to_temporal(self, file_id : str                          ,                 # Save data to temporal cache
                               data     : dict                         ,
                               timestamp: Optional[datetime] = None
                         ) -> bool:
        file_fs = self.file_for_temporal(Safe_Id(file_id), timestamp)
        file_fs.create()
        return file_fs.save(data)
    
    def save_to_both(self, file_id : str                          ,                     # Save to both latest and temporal
                           data     : dict                         ,
                           timestamp: Optional[datetime] = None
                     ) -> bool:
        # Use the combined Memory_FS to save to both paths
        file_fs = self.memory_fs.file__json(Safe_Id(file_id))
        file_fs.create()
        return file_fs.update(data)
    
    def load_from_latest(self, file_id: str                                             # Load data from latest cache
                         ) -> Optional[dict]:
        file_fs = self.file_for_latest(Safe_Id(file_id))
        
        if file_fs.exists():
            return file_fs.content()
        return None
    
    def load_from_temporal(self, file_id : str                          ,               # Load data from temporal cache
                                 timestamp : datetime
                           ) -> Optional[dict]:
        file_fs = self.file_for_temporal(Safe_Id(file_id), timestamp)
        
        if file_fs.exists():
            return file_fs.content()
        return None
    
    def get_latest_metadata(self, file_id: str                                          # Get metadata for latest cache
                            ) -> Optional[Dict[str, Any]]:
        file_fs = self.file_for_latest(Safe_Id(file_id))
        
        if file_fs.exists():
            return file_fs.metadata()
        return None
    
    def delete_latest(self, file_id: str                                                # Delete latest cache entry
                      ) -> bool:
        file_fs = self.file_for_latest(Safe_Id(file_id))
        return file_fs.delete()
    
    def list_temporal_entries(self, file_id_prefix : str                      ,         # List temporal entries by prefix
                                    days_back      : int = 7
                              ) -> list[str]:
        entries = []
        now     = datetime.now()
        
        for day_offset in range(days_back):
            date = datetime(now.year, now.month, now.day)
            date = datetime.fromordinal(date.toordinal() - day_offset)
            
            # Build temporal path
            temporal_path = f"cache/{date.year}/{date.month:02d}/{date.day:02d}"
            
            # List files in temporal path
            folder_files = self.storage_fs.folder__files(temporal_path, return_full_path=True)
            
            for file_path in folder_files:
                if file_id_prefix in str(file_path):
                    entries.append(str(file_path))
        
        return sorted(entries)
    
    def clear_all(self) -> bool:                                                        # Clear all cache entries
        return self.s3__storage.clear()
    
    def clear_old_temporal(self, days_to_keep: int = 30                                 # Clear old temporal entries
                           ) -> int:
        deleted_count = 0
        now           = datetime.now()
        cutoff_date   = datetime.fromordinal(now.toordinal() - days_to_keep)
        
        # Iterate through year/month/day structure
        for year in range(2024, now.year + 1):
            for month in range(1, 13):
                for day in range(1, 32):
                    try:
                        check_date = datetime(year, month, day)
                        if check_date < cutoff_date:
                            path = f"cache/{year}/{month:02d}/{day:02d}"
                            # Delete all files in this day's folders
                            files = self.storage_fs.folder__files(path, return_full_path=True)
                            for file_path in files:
                                if self.storage_fs.file__delete(file_path):
                                    deleted_count += 1
                    except ValueError:
                        continue  # Invalid date, skip
        
        return deleted_count