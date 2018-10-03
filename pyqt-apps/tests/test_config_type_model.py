"""Test config type model."""
import unittest
from unittest import mock

from siriushla.as_ap_pvsconfmgr import ConfigTypeModel


class TestConfigTypeModel(unittest.TestCase):
    """Test ConfigTypeModel."""

    def setUp(self):
        """Set test object."""
        # DB Connection Mock
        self.db = mock.Mock()
        self.db.url = 'FakeURL'
        self.db.get_config_types.return_value = ['T1', 'T2', 'T3']
        self.model = ConfigTypeModel(self.db, None)

    def test_row_count(self):
        """Test row count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.rowCount(index), 4)

    def test_col_count(self):
        """Test column count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.columnCount(index), 1)

    def test_data(self):
        """Test data."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.data(index),
                         'Select a configuration type...')
        index = self.model.createIndex(1, 0)
        self.assertEqual(self.model.data(index), 'T1')
        index = self.model.createIndex(2, 0)
        self.assertEqual(self.model.data(index), 'T2')
        index = self.model.createIndex(3, 0)
        self.assertEqual(self.model.data(index), 'T3')


if __name__ == '__main__':
    unittest.main()
