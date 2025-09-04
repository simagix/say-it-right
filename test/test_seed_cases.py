"""
test_seed_cases.py
@ken.chen
"""
import unittest
from unittest.mock import MagicMock
from seed_cases import seed_cases, load_cases

class TestSeedCases(unittest.TestCase):
    def test_seed_cases_inserts_all(self):
        mock_collection = MagicMock()
        mock_db = MagicMock()
        mock_db.cases = mock_collection
        cases = load_cases()
        # Mock the bulk_write return value
        mock_bulk_write_result = MagicMock()
        mock_bulk_write_result.upserted_count = len(cases)
        mock_bulk_write_result.modified_count = 0
        mock_collection.bulk_write.return_value = mock_bulk_write_result
        count = seed_cases(mock_db)
        self.assertEqual(count, len(cases))
        self.assertEqual(mock_collection.bulk_write.call_count, 1)

if __name__ == "__main__":
    unittest.main()
