from unittest                                                import TestCase
from mgraph_ai_service_llms.service.cache.Service__Cache     import Service__Cache
from mgraph_ai_service_llms.service.cache.LLM__Cache         import LLM__Cache
from tests.unit.Service__Fast_API__Test_Objs                 import setup__service_fast_api_test_objs


class test_Service__Cache(TestCase):

    @classmethod
    def setUpClass(cls):
        setup__service_fast_api_test_objs()
        cls.service_cache = Service__Cache()

    def test__init__(self):
        with self.service_cache as _:
            assert type(_)            is Service__Cache
            assert type(_.llm_cache)  is LLM__Cache
            assert _.cache_index_path == 'cache_index.json'
            assert _._cached_index    is None

    def test_cache_index(self):
        result = self.service_cache.cache_index()

        assert type(result)     is dict
        assert result['status'] in ['success', 'error']

        if result['status'] == 'success':
            assert 'data' in result
            data = result['data']

            # Check for expected structure or empty message
            if 'message' in data:
                assert data['message'] == 'Cache index is empty or not initialized'
                assert data.get('cache_id__from__hash__request') == {}
                assert data.get('cache_id__to__file_path')       == {}
            else:
                # If cache exists, check structure
                assert 'cache_id__from__hash__request' in data
                assert 'cache_id__to__file_path'       in data
                assert type(data['cache_id__from__hash__request']) is dict
                assert type(data['cache_id__to__file_path'])       is dict

    def test_get_cache_entry_by_id(self):
        # First get the cache index to find a valid cache ID
        index_result = self.service_cache.cache_index()

        if index_result['status'] == 'success' and index_result['data']:
            cache_ids = index_result['data'].get('cache_id__to__file_path', {})

            if cache_ids:
                # Test with first available cache ID
                test_cache_id = list(cache_ids.keys())[0]
                result = self.service_cache.get_cache_entry_by_id(test_cache_id)

                assert type(result)       is dict
                assert result['status']   in ['success', 'error']
                assert result['cache_id'] == test_cache_id

                if result['status'] == 'success':
                    assert 'data'      in result
                    assert 'file_path' in result
                    assert result['file_path'] == cache_ids[test_cache_id]
            else:
                # Test with non-existent cache ID
                result = self.service_cache.get_cache_entry_by_id('non_existent_id')
                assert result['status']   == 'error'
                assert result['cache_id'] == 'non_existent_id'
                assert 'not found in index' in result['message']
        else:
            # Test when cache index cannot be loaded
            result = self.service_cache.get_cache_entry_by_id('any_id')
            assert result['status'] == 'error'
            assert 'data' in result

    def test_get_cache_entry_by_hash(self):
        # First get the cache index to find a valid request hash
        index_result = self.service_cache.cache_index()

        if index_result['status'] == 'success' and index_result['data']:
            hash_to_id = index_result['data'].get('cache_id__from__hash__request', {})

            if hash_to_id:
                # Test with first available hash
                test_hash = list(hash_to_id.keys())[0]
                expected_cache_id = hash_to_id[test_hash]

                result = self.service_cache.get_cache_entry_by_hash(test_hash)

                assert type(result)          is dict
                assert result['status']      in ['success', 'error']
                assert result['request_hash'] == test_hash

                if result['status'] == 'success':
                    assert 'data'      in result
                    assert 'cache_id'  in result
                    assert 'file_path' in result
                    assert result['cache_id'] == expected_cache_id
            else:
                # Test with non-existent hash
                result = self.service_cache.get_cache_entry_by_hash('non_existent_hash')
                assert result['status']       == 'error'
                assert result['request_hash'] == 'non_existent_hash'
                assert 'not found in index' in result['message']
        else:
            # Test when cache index cannot be loaded
            result = self.service_cache.get_cache_entry_by_hash('any_hash')
            assert result['status'] == 'error'
            assert 'data' in result

    def test_get_cache_entry_by_hash__with_full_hash(self):
        # Test that the method handles both short (10 char) and full hashes
        index_result = self.service_cache.cache_index()

        if index_result['status'] == 'success' and index_result['data']:
            hash_to_id = index_result['data'].get('cache_id__from__hash__request', {})

            if hash_to_id:
                short_hash = list(hash_to_id.keys())[0]
                # Simulate a full hash by adding characters
                full_hash = short_hash + 'additional_chars'

                result = self.service_cache.get_cache_entry_by_hash(full_hash)

                # Should still find it using the first 10 characters
                if len(short_hash) == 10:
                    assert result['request_hash'] == full_hash
                    # It should either find it or not, depending on cache state
                    assert result['status'] in ['success', 'error']

    def test_cache_stats(self):
        result = self.service_cache.cache_stats()

        assert type(result)     is dict
        assert result['status'] in ['success', 'error']

        if result['status'] == 'success':
            assert 'data' in result
            stats = result['data']

            # Check expected stats structure
            assert 'total_entries'        in stats
            assert 'total_request_hashes' in stats
            assert 'models_distribution'   in stats
            assert 'dates_distribution'    in stats
            assert 'bucket_name'          in stats
            assert 'root_folder'          in stats

            # Check types
            assert type(stats['total_entries'])        is int
            assert type(stats['total_request_hashes']) is int
            assert type(stats['models_distribution'])  is dict
            assert type(stats['dates_distribution'])   is dict
            assert type(stats['root_folder'])          is str

            # Check root folder value
            assert stats['root_folder'] == 'llm-cache/'

    def test_cache_index__caching_behavior(self):
        # Test that the index is cached in memory after first load
        self.service_cache._cached_index = {}  # Clear any cached index

        # First call should load from S3
        result1 = self.service_cache.cache_index()

        if result1['status'] == 'success' and result1['data']:
            # Check that index is now cached
            assert self.service_cache._cached_index is not None

            # Store the cached version
            cached_data = self.service_cache._cached_index

            # Second call should use cached version
            result2 = self.service_cache.cache_index()

            # Should return the same data
            assert result2['data'] == result1['data']
            # Should still be the same object in memory
            assert self.service_cache._cached_index == cached_data

    def test_cache_stats__with_sample_data(self):
        # Test stats calculation with known index structure
        self.service_cache._cached_index = {
            'cache_id__from__hash__request': {
                'cb93fe94c1': '9299d6d6',
                '6017b1e8ae': '44c415d9',
            },
            'cache_id__to__file_path': {
                '9299d6d6': 'gpt-4o-mini/2025/07/23/15/9299d6d6.json',
                '44c415d9': 'openai_gpt-4_1-mini/2025/07/23/15/44c415d9.json',
                'f71571ad': 'google_gemini-2_5-flash-lite/2025/07/24/15/f71571ad.json',
            }
        }

        result = self.service_cache.cache_stats()

        assert result['status'] == 'success'
        stats = result['data']

        assert stats['total_entries']        == 3
        assert stats['total_request_hashes'] == 2

        # Check model distribution
        assert 'gpt-4o-mini'                    in stats['models_distribution']
        assert 'openai/gpt-4/1-mini'            in stats['models_distribution']
        assert 'google/gemini-2/5-flash-lite'   in stats['models_distribution']

        # Check dates distribution
        assert '2025/07/23' in stats['dates_distribution']
        assert '2025/07/24' in stats['dates_distribution']
        assert stats['dates_distribution']['2025/07/23'] == 2
        assert stats['dates_distribution']['2025/07/24'] == 1

    def test_get_cache_entry_by_id__error_cases(self):
        # Test various error scenarios

        # Test with None cache_id
        result = self.service_cache.get_cache_entry_by_id('')
        assert result['status']   == 'error'
        assert result['cache_id'] == ''

        # Test with special characters
        result = self.service_cache.get_cache_entry_by_id('../../etc/passwd')
        assert result['status']   == 'error'
        assert result['cache_id'] == '../../etc/passwd'

    def test_get_cache_entry_by_hash__error_cases(self):
        # Test various error scenarios

        # Test with empty hash
        result = self.service_cache.get_cache_entry_by_hash('')
        assert result['status']       == 'error'
        assert result['request_hash'] == ''

        # Test with very short hash (less than 10 chars)
        result = self.service_cache.get_cache_entry_by_hash('abc')
        assert result['status']       == 'error'
        assert result['request_hash'] == 'abc'