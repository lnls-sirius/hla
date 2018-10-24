"""Test PVConfigurationTableModel class."""
import unittest
from unittest import mock

from numpy import array

from siriushla.as_ap_pvsconfmgr import PVConfigurationTableModel

path = 'siriushla.as_ap_pvsconfmgr'
fake_url = 'FakeURL'
pvs = [['SI-01M1:MA-CH:PwrState-Sel', 1],
       ['SI-01M1:MA-CH:Current-SP', 1.0],
       ['SI-01M1:MA-CH:OpMode-Sel', 'SlowRef'],
       ['SI-02M1:MA-CH:PwrState-Sel', False],
       ['SI-02M1:MA-CH:OpMode-Sel', array(list(range(10)))]]
ret_pvs = [['SI-01M1:MA-CH:PwrState-Sel', 2],
           ['SI-01M1:MA-CH:Current-SP', 2.0],
           ['SI-01M1:MA-CH:OpMode-Sel', 'SlowRefSync'],
           ['SI-02M1:MA-CH:PwrState-Sel', True],
           ['SI-02M1:MA-CH:OpMode-Sel', array(list(range(1, 11)))]]


class TestPVConfigurationTableModelInit(unittest.TestCase):
    """Test Model behavior."""

    def setUp(self):
        """Setup."""
        self.model = PVConfigurationTableModel(None, None)

    def test_row_count(self):
        """Test row count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.rowCount(index), 0)

    def test_col_count(self):
        """Test column count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.columnCount(index), 0)

    def test_data(self):
        """Test model data."""
        index = self.model.createIndex(0, 0)
        with self.assertRaises(IndexError):
            self.model.data(index)


class TestPVConfigurationTableModelSetConfigType(unittest.TestCase):
    """Test Model behavior."""

    def setUp(self):
        """Setup."""
        # Mock get_config_template
        get_config_template_path = path + \
            '.pv_configuration_model.get_config_type_template'
        ct_patch = mock.patch(get_config_template_path)
        self.addCleanup(ct_patch.stop)
        self.ct_mock = ct_patch.start()
        self.ct_mock.return_value = {'pvs': pvs}
        self.model = PVConfigurationTableModel(None, None)
        self.model.config_type = 'Faketype'

    def test_row_count(self):
        """Test row count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.rowCount(index), len(pvs))

    def test_col_count(self):
        """Test column count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.columnCount(index), len(pvs[0]))

    def test_data(self):
        """Test model data."""
        for i in range(5):
            for j in range(2):
                index = self.model.createIndex(i, j)
                try:
                    self.assertEqual(self.model.data(index), pvs[i][j])
                except ValueError:  # ndarray
                    self.assertTrue(
                            (self.model.data(index) == pvs[i][j]).all())

    def test_set_data_pv_column(self):
        """Test setting data."""
        index = self.model.createIndex(0, 0)
        self.assertFalse(self.model.setData(index, 'FakePv'))
        self.assertEqual(self.model.data(index), pvs[0][0])

    def test_set_data_value_column(self):
        """Test setting data."""
        index = self.model.createIndex(0, 1)
        self.assertTrue(self.model.setData(index, 2))
        self.assertEqual(self.model.data(index), 2)


class TestPVConfigurationTableModelSetInvalidConfig(unittest.TestCase):
    """Test Model behavior."""

    def setUp(self):
        """Setup."""
        # Mock get_config_template
        get_config_template_path = path + \
            '.pv_configuration_model.get_config_type_template'
        ct_patch = mock.patch(get_config_template_path)
        self.addCleanup(ct_patch.stop)
        self.ct_mock = ct_patch.start()
        self.ct_mock.return_value = {'not_pvs': pvs}
        self.model = PVConfigurationTableModel(None, None)
        self.model.config_type = 'Faketype'

    def test_row_count(self):
        """Test row count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.rowCount(index), 0)

    def test_col_count(self):
        """Test column count."""
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.columnCount(index), 0)

    def test_data(self):
        """Test model data."""
        index = self.model.createIndex(0, 0)
        with self.assertRaises(IndexError):
            self.model.data(index)


if __name__ == '__main__':
    unittest.main()
