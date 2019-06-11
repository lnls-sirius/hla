"""Test config type model."""
import unittest
from unittest import mock

from siriushla.as_ap_configdb.pvsconfigs import ConfigNamesModel


class TestConfigTypeModelInitialization(unittest.TestCase):
    """Test ConfigTypeModel."""

    def setUp(self):
        """Set test object."""
        # DB Connection Mock
        self.db = mock.Mock()
        self.db.url = 'FakeURL'
        self.model = ConfigNamesModel(self.db, None)

    def test_row_count(self):
        """Test row count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.rowCount(index), 1)

    def test_col_count(self):
        """Test column count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.columnCount(index), 1)

    def test_data(self):
        """Test data."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.data(index),
                         'No configuration found...')
        index = self.model.createIndex(1, 0)
        with self.assertRaises(IndexError):
            self.assertEqual(self.model.data(index), 'N1')


class TestConfigTypeModelSetConfigType(unittest.TestCase):
    """Test ConfigTypeModel."""

    def setUp(self):
        """Set test object."""
        # DB Connection Mock
        self.db = mock.Mock()
        self.db.url = 'FakeURL'
        self.db.get_names_by_type.return_value = \
            {'code': 200, 'result': ['N1', 'N2', 'N3']}
        self.model = ConfigNamesModel(self.db, None)
        self.model.config_type = 'FakeConfig'

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
                         'Select a configuration...')
        index = self.model.createIndex(1, 0)
        self.assertEqual(self.model.data(index), 'N1')
        index = self.model.createIndex(2, 0)
        self.assertEqual(self.model.data(index), 'N2')
        index = self.model.createIndex(3, 0)
        self.assertEqual(self.model.data(index), 'N3')


class TestConfigTypeModelSetConfigTypeFailure(unittest.TestCase):
    """Test ConfigTypeModel."""

    def setUp(self):
        """Set test object."""
        # DB Connection Mock
        self.db = mock.Mock()
        self.db.url = 'FakeURL'
        self.db.get_names_by_type.return_value = \
            {'code': 400, 'message': 'FakeError'}
        self.model = ConfigNamesModel(self.db, None)
        self.model.config_type = 'FakeConfig'

    def test_row_count(self):
        """Test row count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.rowCount(index), 1)

    def test_col_count(self):
        """Test column count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.columnCount(index), 1)

    def test_data(self):
        """Test data."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.data(index),  'FakeError')

if __name__ == '__main__':
    unittest.main()
