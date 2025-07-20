import unittest
from main import HashIndex, linear_search, generate_keys
import random

# Unit tests for the HashIndex class
class TestHashIndex(unittest.TestCase):

    def setUp(self):
        # Create a hash index and insert 50 key-value pairs before each test
        self.index = HashIndex(100)
        self.sample_data = [(i, f"value_{i}") for i in range(50)]
        for key, val in self.sample_data:
            self.index.insert(key, val)

    def test_hash_insertion_and_collision(self):
        # Ensure the hash table has the correct number of buckets
        self.assertEqual(len(self.index.table), 100)

        # Confirm all inserted entries exist in the hash table
        total_entries = sum(len(bucket) for bucket in self.index.table)
        self.assertEqual(total_entries, 50)

        # Check that collision count is non-negative (i.e., collisions tracked properly)
        self.assertGreaterEqual(self.index.collisions, 0)

    def test_hash_search_success(self):
        # Verify that searching for existing keys returns correct values
        for key, val in self.sample_data:
            result = self.index.search(key)
            self.assertEqual(result, val)

    def test_hash_search_missing(self):
        # Searching for keys not in the table should return None
        self.assertIsNone(self.index.search(1000))
        self.assertIsNone(self.index.search(-1))


# Unit tests for the linear_search function
class TestLinearSearch(unittest.TestCase):

    def setUp(self):
        # Create a sample dataset for linear search
        self.data = [(i, f"value_{i}") for i in range(20)]

    def test_linear_search_found(self):
        # Ensure that linear search returns correct key-value pairs when found
        for key, val in self.data:
            result = linear_search(self.data, key)
            self.assertEqual(result, (key, val))

    def test_linear_search_not_found(self):
        # Searching for keys not in the dataset should return None
        self.assertIsNone(linear_search(self.data, 100))
        self.assertIsNone(linear_search(self.data, -5))


# Unit tests for the generate_keys function (used for access patterns)
class TestKeyGeneration(unittest.TestCase):

    def setUp(self):
        # Prepare a sample list of data_ids to generate keys from
        self.data_ids = [f"id_{i}" for i in range(100)]

    def test_random_pattern(self):
        # Test random access pattern returns correct number of valid keys
        keys = generate_keys(self.data_ids, 'random', 10)
        self.assertEqual(len(keys), 10)
        self.assertTrue(all(k in self.data_ids for k in keys))

    def test_sequential_pattern(self):
        # Sequential pattern should return the first 'n' items in order
        keys = generate_keys(self.data_ids, 'sequential', 10)
        self.assertEqual(keys, self.data_ids[:10])

    def test_clustered_pattern(self):
        # Clustered pattern should return 'n' valid keys from a specific subset
        keys = generate_keys(self.data_ids, 'clustered', 10)
        self.assertEqual(len(keys), 10)
        self.assertTrue(all(k in self.data_ids for k in keys))

    def test_mixed_pattern(self):
        # Mixed pattern should return 'n' valid keys of random mix
        keys = generate_keys(self.data_ids, 'mixed', 10)
        self.assertEqual(len(keys), 10)

    def test_missing_pattern(self):
        # Missing pattern should return keys that do not exist in the dataset
        keys = generate_keys(self.data_ids, 'missing', 5)
        self.assertEqual(keys, [f"MISSING_{i}" for i in range(5)])

    def test_invalid_pattern(self):
        # Invalid access pattern should return an empty list
        keys = generate_keys(self.data_ids, 'invalid', 5)
        self.assertEqual(keys, [])


# Run the test suite from command line or IDE
if __name__ == "__main__":
    unittest.main()
