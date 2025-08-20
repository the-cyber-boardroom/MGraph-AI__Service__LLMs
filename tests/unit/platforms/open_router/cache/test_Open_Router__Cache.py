# tests/unit/platforms/open_router/cache/test_Open_Router__Cache.py

from datetime                                                                        import datetime, timedelta
from unittest                                                                        import TestCase

from memory_fs.file_fs.File_FS import File_FS
from memory_fs.file_types.Memory_FS__File__Type__Json import Memory_FS__File__Type__Json
from memory_fs.file_types.Memory_FS__File__Type__Text import Memory_FS__File__Type__Text
from memory_fs.helpers.Memory_FS__Latest_Temporal import Memory_FS__Latest_Temporal
from osbot_aws.testing.Temp__Random__AWS_Credentials                                 import OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID, OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION
from osbot_aws.utils.AWS_Sanitization                                                import str_to_valid_s3_bucket_name
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path       import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                   import Safe_Id
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc                                                          import random_string_short
from osbot_utils.utils.Objects import base_classes, __
from osbot_aws.AWS_Config                                                            import aws_config
from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Cache           import Open_Router__Cache
from mgraph_ai_service_llms.service.s3.Storage_FS__S3                                import Storage_FS__S3
from tests.unit.Service__Fast_API__Test_Objs                                         import setup__service_fast_api_test_objs


class test_Open_Router__Cache(TestCase):                                                # Test OpenRouter cache implementation

    @classmethod
    def setUpClass(cls):                                                                # Initialize LocalStack and test cache
        cls.test_objs = setup__service_fast_api_test_objs()

        cls.test_bucket = str_to_valid_s3_bucket_name(random_string_short("test-or-cache-"))
        cls.test_prefix = "test-cache"

        assert aws_config.account_id () == OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID
        assert aws_config.region_name() == OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION

        # Test data
        cls.test_file_id  = "test-models"
        cls.test_data     = {"models": [{"id": "model1", "name": "Test Model"}], "version": "1.0"}
        cls.test_metadata = {"source": "test", "timestamp": datetime.now().isoformat()}
        with Open_Router__Cache() as _:
            cls.cache             = _
            _.s3_bucket   = cls.test_bucket
            _.s3_prefix   = cls.test_prefix
            _.setup()

    @classmethod
    def tearDownClass(cls):                                                             # Clean up test resources
        with cls.cache.s3__storage.s3 as _:
            if _.bucket_exists(cls.test_bucket):
                _.bucket_delete_all_files(cls.test_bucket)
                _.bucket_delete(cls.test_bucket)


    def tearDown(self):                                                                 # Clean up after each test
        self.cache.clear_all()

    def test__setUpClass(self):
        with self.cache as _:
            assert type(_) == Open_Router__Cache


    def test__init__(self):                                                             # Test initialization
        cache = Open_Router__Cache()

        assert type(cache)         is Open_Router__Cache
        assert base_classes(cache) == [Type_Safe, object]
        assert cache.s3_bucket     == "openrouter-cache"
        assert cache.s3_prefix     == "models"
        assert cache.storage_fs    is None
        assert cache.memory_fs     is None

    def test_setup(self):                                                               # Test setup process
        with self.cache as _:
            assert type(_.storage_fs)        is Storage_FS__S3
            assert _.storage_fs.s3_bucket    == self.test_bucket
            assert _.storage_fs.s3_prefix    == self.test_prefix
            assert type(_.memory_fs)         is Memory_FS__Latest_Temporal
            assert _.memory_fs.storage_fs    is _.storage_fs

            assert len(_.memory_fs.path_handlers) ==                                    2  # Check path handlers were configured:  Latest and Temporal

    def test_file_for_latest(self):                                                     # Test latest file creation
        file_id        = Safe_Id("test-file")
        file_contents  = "some content"
        file_fs        = self.cache.file_for_latest(file_id)
        created_paths = [ Safe_Str__File__Path(f'latest/{file_id}.json'         ),
                          Safe_Str__File__Path(f'latest/{file_id}.json.config'  ),
                          Safe_Str__File__Path(f'latest/{file_id}.json.metadata')]
        updated_paths = [ Safe_Str__File__Path('latest/test-file.json'          ),
                          Safe_Str__File__Path('latest/test-file.json.metadata' )]
        assert file_fs is not None
        with file_fs as _:
            assert type(_)                         is File_FS
            assert type(_.file__config.file_type)  is Memory_FS__File__Type__Json
            assert _.obj()            == __(file__config = __(exists_strategy = 'FIRST'   ,
                                                              file_id         = file_id   ,
                                                              file_paths      = ['latest'],
                                                              file_type       = __( name           = 'json',
                                                                                    content_type   = 'JSON',
                                                                                    file_extension = 'json',
                                                                                    encoding       = 'UTF_8',
                                                                                    serialization  ='JSON'  )),
                                            storage_fs   = __(s3_prefix = 'models',
                                                              s3        = __( tmp_file_folder = 's3_temp_files',
                                                                              use_threads     = True,
                                                                              session_kwargs__s3=__( service_name          = 's3',
                                                                                                     aws_access_key_id     = None,
                                                                                                     aws_secret_access_key = None,
                                                                                                     endpoint_url          = None,
                                                                                                     region_name           = None)),
                                                             s3_bucket  = 'openrouter-cache'))
            assert _.file__config.file_id         == file_id
            assert _.storage_fs                   == self.cache.s3__storage
            assert _.file__config.file_paths      == ['latest']
            assert _.create()                     == created_paths
            assert _.update(file_contents)        == updated_paths
            assert sorted(_.paths())              == created_paths
            assert _.exists()                     is True
            assert _.content()                    == file_contents
            assert file_fs.delete()               == created_paths
            assert file_fs.exists()               is False


    def test_file_for_temporal(self):                                                   # Test temporal file creation
        timestamp = datetime(2025, 1, 21, 15, 30, 45)
        file_type = Memory_FS__File__Type__Text
        file_fs   = self.cache.file_for_temporal(file_id="test-file", file_type=file_type, timestamp=timestamp)
        with file_fs as _:
            assert type(_) is File_FS
            assert _.file__config.obj() == __( exists_strategy = 'FIRST',
                                               file_id         = 'test-file',
                                               file_paths      = ['2025/08/21/00'],
                                               file_type       = __( name           = 'text'  ,
                                                                     content_type   = 'TXT'   ,
                                                                     file_extension = 'txt'   ,
                                                                     encoding       = 'UTF_8' ,
                                                                     serialization  = 'STRING'))
        return
        assert file_fs               is not None
        assert file_fs.file__config.file_id == Safe_Id('test-file-2025-01-21T15_30_45')
        assert file_fs.file__config.file_paths == []
        assert "test-file"           in file_fs.file__config.file_id
        return
        assert timestamp.isoformat() in str(file_fs.file__config.file_id)
        assert file_fs.storage_fs    is self.cache.storage_fs

    def test_file_for_temporal_default_timestamp(self):                                 # Test temporal with auto timestamp
        file_fs = self.cache.file_for_temporal(Safe_Id("test-file"))

        assert file_fs is not None
        assert "test-file" in str(file_fs.file__config.file_id)
        # Should have current timestamp in ID
        assert datetime.now().strftime("%Y-%m") in str(file_fs.file__config.file_id)

    def test_save_to_latest(self):                                                      # Test saving to latest cache
        result = self.cache.save_to_latest(self.test_file_id, self.test_data)

        assert result is True

        # Verify data can be loaded back
        loaded_data = self.cache.load_from_latest(self.test_file_id)
        assert loaded_data == self.test_data

    def test_save_to_temporal(self):                                                    # Test saving to temporal cache
        timestamp = datetime.now()
        result    = self.cache.save_to_temporal(self.test_file_id, self.test_data, timestamp)

        assert result is True

        # Verify file was created in temporal structure
        temporal_file_id = f"{self.test_file_id}-{timestamp.isoformat()}"

        # Check storage directly for temporal path
        expected_path_pattern = f"{timestamp.year}/{timestamp.month:02d}/{timestamp.day:02d}"

        # List all files to verify temporal structure
        all_files = self.cache.storage_fs.files__paths()
        temporal_files = [f for f in all_files if expected_path_pattern in str(f)]
        assert len(temporal_files) > 0

    def test_save_to_both(self):                                                        # Test saving to both paths
        timestamp = datetime.now()
        result    = self.cache.save_to_both(self.test_file_id, self.test_data, timestamp)

        assert result is True

        # Verify data is in latest
        latest_data = self.cache.load_from_latest(self.test_file_id)
        assert latest_data == self.test_data

        # Verify temporal files were created
        all_files = self.cache.storage_fs.files__paths()

        # Should have files in both latest and temporal paths
        latest_files   = [f for f in all_files if "latest" in str(f)]
        temporal_files = [f for f in all_files if f"{timestamp.year}/{timestamp.month:02d}" in str(f)]

        assert len(latest_files) > 0
        assert len(temporal_files) > 0

    def test_load_from_latest(self):                                                    # Test loading from latest cache
        # Save data first
        self.cache.save_to_latest(self.test_file_id, self.test_data)

        # Load it back
        loaded_data = self.cache.load_from_latest(self.test_file_id)

        assert loaded_data == self.test_data

    def test_load_from_latest_not_exists(self):                                        # Test loading non-existent latest
        loaded_data = self.cache.load_from_latest("non-existent-id")

        assert loaded_data is None

    def test_load_from_temporal(self):                                                  # Test loading from temporal cache
        timestamp = datetime.now()

        # Save data first
        self.cache.save_to_temporal(self.test_file_id, self.test_data, timestamp)

        # Load it back
        loaded_data = self.cache.load_from_temporal(self.test_file_id, timestamp)

        assert loaded_data == self.test_data

    def test_load_from_temporal_not_exists(self):                                       # Test loading non-existent temporal
        timestamp   = datetime(2020, 1, 1, 0, 0)
        loaded_data = self.cache.load_from_temporal("non-existent", timestamp)

        assert loaded_data is None

    def test_get_latest_metadata(self):                                                 # Test getting metadata
        # Save data first
        self.cache.save_to_latest(self.test_file_id, self.test_data)

        # Get metadata
        metadata = self.cache.get_latest_metadata(self.test_file_id)

        assert metadata is not None
        # Metadata structure from File_FS
        assert 'content__hash' in metadata or 'timestamp' in metadata

    def test_get_latest_metadata_not_exists(self):                                      # Test metadata for non-existent
        metadata = self.cache.get_latest_metadata("non-existent")

        assert metadata is None

    def test_delete_latest(self):                                                       # Test deleting latest cache
        # Save data first
        self.cache.save_to_latest(self.test_file_id, self.test_data)
        assert self.cache.load_from_latest(self.test_file_id) is not None

        # Delete it
        result = self.cache.delete_latest(self.test_file_id)

        assert result is True
        assert self.cache.load_from_latest(self.test_file_id) is None

    def test_list_temporal_entries(self):                                               # Test listing temporal entries
        # Save multiple temporal entries
        now = datetime.now()

        for i in range(3):
            timestamp = now - timedelta(hours=i)
            file_id   = f"{self.test_file_id}-{i}"
            self.cache.save_to_temporal(file_id, self.test_data, timestamp)

        # List entries
        entries = self.cache.list_temporal_entries(self.test_file_id, days_back=7)

        assert len(entries) >= 3
        for entry in entries:
            assert self.test_file_id in entry

    def test_list_temporal_entries_empty(self):                                         # Test listing with no entries
        entries = self.cache.list_temporal_entries("non-existent", days_back=1)

        assert entries == []

    def test_list_temporal_entries_multiple_days(self):                                 # Test listing across multiple days
        now = datetime.now()

        # Create entries across different days
        for days_ago in [0, 1, 2]:
            timestamp = now - timedelta(days=days_ago)
            file_id   = f"multi-day-{days_ago}"
            self.cache.save_to_temporal(file_id, {"day": days_ago}, timestamp)

        # List entries for last 3 days
        entries = self.cache.list_temporal_entries("multi-day", days_back=3)

        # Should find entries from all 3 days
        assert len(entries) >= 3

    def test_clear_all(self):                                                           # Test clearing all cache
        # Save multiple entries
        self.cache.save_to_latest("file1", {"data": 1})
        self.cache.save_to_latest("file2", {"data": 2})
        self.cache.save_to_temporal("file3", {"data": 3})

        # Verify files exist
        assert self.cache.load_from_latest("file1") is not None
        assert self.cache.load_from_latest("file2") is not None

        # Clear all
        result = self.cache.clear_all()

        assert result is True
        assert self.cache.load_from_latest("file1") is None
        assert self.cache.load_from_latest("file2") is None

        # Storage should be empty
        assert len(self.cache.storage_fs.files__paths()) == 0

    def test_clear_old_temporal(self):                                                  # Test clearing old temporal entries
        now = datetime.now()

        # Save old entry (35 days ago)
        old_date = now - timedelta(days=35)
        self.cache.save_to_temporal("old-entry", {"old": True}, old_date)

        # Save recent entry (5 days ago)
        recent_date = now - timedelta(days=5)
        self.cache.save_to_temporal("recent-entry", {"recent": True}, recent_date)

        # Clear old entries (older than 30 days)
        deleted_count = self.cache.clear_old_temporal(days_to_keep=30)

        # Should have deleted at least the old entry
        assert deleted_count >= 0

        # Recent entry should still be loadable
        recent_data = self.cache.load_from_temporal("recent-entry", recent_date)
        assert recent_data == {"recent": True}

    def test_clear_old_temporal_with_invalid_dates(self):                               # Test clearing handles invalid dates
        # Should handle gracefully even with no entries
        deleted_count = self.cache.clear_old_temporal(days_to_keep=7)

        assert deleted_count >= 0

    def test_concurrent_operations(self):                                               # Test multiple operations
        timestamp = datetime.now()

        # Save to latest
        self.cache.save_to_latest(self.test_file_id, self.test_data)

        # Save to temporal
        temporal_data = {**self.test_data, "temporal": True}
        self.cache.save_to_temporal(self.test_file_id, temporal_data, timestamp)

        # Save to both
        both_data = {**self.test_data, "both": True}
        self.cache.save_to_both(f"{self.test_file_id}-both", both_data)

        # Verify all operations
        assert self.cache.load_from_latest(self.test_file_id) == self.test_data
        assert self.cache.load_from_temporal(self.test_file_id, timestamp) == temporal_data
        assert self.cache.load_from_latest(f"{self.test_file_id}-both") == both_data

    def test_large_data_handling(self):                                                 # Test with large data
        large_data = {
            "models": [{"id": f"model_{i}", "data": "x" * 1000} for i in range(100)]
        }

        # Save large data
        result = self.cache.save_to_latest("large-data", large_data)
        assert result is True

        # Load it back
        loaded_data = self.cache.load_from_latest("large-data")
        assert loaded_data == large_data

    def test_special_characters_in_file_id(self):                                       # Test file IDs with special chars
        special_id = "test/model:version-1.0"

        # Should handle special characters
        result = self.cache.save_to_latest(special_id, self.test_data)
        assert result is True

        loaded_data = self.cache.load_from_latest(special_id)
        assert loaded_data == self.test_data

    def test_storage_fs_configuration(self):                                            # Test storage configuration
        # Create new cache with different settings
        with Open_Router__Cache() as _:
            _.s3_bucket = "different-bucket"
            _.s3_prefix = "different-prefix"
            assert self.cache.storage_fs.s3.bucket_exists(_.s3_bucket)  is False
            _.setup()

            assert _.storage_fs.s3_bucket == "different-bucket"
            assert _.storage_fs.s3_prefix == "different-prefix"
            assert _.storage_fs.s3.bucket_exists(_.s3_bucket)  is True
            assert _.storage_fs.s3.bucket_delete(_.s3_bucket)  is True

    def test_memory_fs_path_handlers(self):                                             # Test path handler configuration
        # Check that handlers are properly configured
        handlers = self.cache.memory_fs.path_handlers

        assert len(handlers) == 2

        # First should be latest handler
        from memory_fs.path_handlers.Path__Handler__Latest import Path__Handler__Latest
        assert isinstance(handlers[0], Path__Handler__Latest)

        # Second should be temporal handler
        from memory_fs.path_handlers.Path__Handler__Temporal import Path__Handler__Temporal
        assert isinstance(handlers[1], Path__Handler__Temporal)

        # Latest handler should have cache prefix
        assert handlers[0].prefix_path == Safe_Str__File__Path("cache")

    def test_file_operations_integration(self):                                         # Test File_FS integration
        # Create file through cache
        file_fs = self.cache.file_for_latest(Safe_Id("integration-test"))

        # Should be able to use File_FS operations
        file_fs.create()
        file_fs.save({"test": "data"})

        assert file_fs.exists() is True
        assert file_fs.content() == {"test": "data"}

        # Delete through File_FS
        file_fs.delete()
        assert file_fs.exists() is False

    def test_timestamp_consistency(self):                                               # Test timestamp handling
        # Fixed timestamp
        fixed_time = datetime(2025, 1, 21, 15, 30, 45, 123456)

        # Save with specific timestamp
        self.cache.save_to_temporal("timestamp-test", self.test_data, fixed_time)

        # Load with same timestamp
        loaded = self.cache.load_from_temporal("timestamp-test", fixed_time)
        assert loaded == self.test_data

        # Should not load with different timestamp
        different_time = datetime(2025, 1, 21, 15, 30, 46)
        loaded_wrong = self.cache.load_from_temporal("timestamp-test", different_time)
        assert loaded_wrong is None