"""Test ReadConfigurationWindow."""
import unittest
from unittest import mock
from numpy import array, ndarray

from qtpy.QtWidgets import QComboBox, QLabel, QPushButton, QTableView

from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_configdb.pvsconfigs import ReadConfigurationWindow

path = 'siriushla.as_ap_configdb.pvsconfigs'
fake_url = 'FakeURL'
db_types_ret = ['Type1', 'Type2']
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
configs = {
    'Type1': {
        'config_name': 'Type1',
        'value': {'pvs': pvs}},
    'Type2': {
        'config_name': 'Type2',
        'value': {'not_pvs': []}}
    }


def get_template(config_type):
    """get_config_template side effects mock function."""
    return configs[config_type]['value']


class MockWrapper:

    def __init__(self, pv):
        self.pvname = pv

    def get(self):
        for pv, value in ret_pvs:
            if pv == self.pvname:
                return value
        return None


def init_window(obj):
    """Initiale window."""
    # DB Connection Mock
    obj.db = mock.Mock()
    obj.db.url = fake_url
    obj.db.get_config_types.return_value = db_types_ret
    # Epics wrapper Mock
    obj.wrapper = MockWrapper
    # Test object
    obj._app = SiriusApplication()
    obj._window = ReadConfigurationWindow(obj.db, obj.wrapper)
    # Get widgets
    obj.cb = obj._window.findChild(QComboBox, 'type_cb')
    obj.rb = obj._window.findChild(QPushButton, 'read_btn')
    obj.tv = obj._window.findChild(QTableView, 'config_tbl')
    obj.sb = obj._window.findChild(QPushButton, 'save_btn')


def mock_get_config_template_path(obj):
    """Mock get_config_template function."""
    get_config_template_path = path + \
        '.pv_configuration_model.get_config_type_template'
    # Mock get_config_template
    ct_patch = mock.patch(get_config_template_path)
    obj.addCleanup(ct_patch.stop)
    obj.ct_mock = ct_patch.start()
    obj.ct_mock.side_effect = get_template


class TestWindowSetup(unittest.TestCase):
    """Test initial setup of ReadConfigurationWindow.

    QComboBox - Display a message
    Read Button - Disabled
    QTableView - Empty
    Save Button - Disabled
    """

    def setUp(self):
        """Common method for all test."""
        init_window(self)

    def test_combo_box(self):
        """Test combo box is correctly initialized."""
        cb = self._window.findChild(QComboBox, 'type_cb')
        self.assertEqual(cb.count(), len(db_types_ret) + 1)

    def test_read_button(self):
        """Test read button is disabled."""
        rb = self._window.findChild(QPushButton, 'read_btn')
        self.assertFalse(rb.isEnabled())

    def test_table_view(self):
        """Test table view is empty."""
        tv = self._window.findChild(QTableView, 'config_tbl')
        d = tv.model().model_data
        self.assertEqual(d, list())

    def test_save_button(self):
        """Test save button is disabled."""
        sb = self._window.findChild(QPushButton, 'save_btn')
        self.assertFalse(sb.isEnabled())


class TestSelectConfigType(unittest.TestCase):
    """Test selecting a config type.

    config has field 'pvs'
        read button is enabled
        table view is filled
    config has not field 'pvs'
        read button is not enabled
        table is not filled
    """

    def setUp(self):
        """Common method for all test."""
        mock_get_config_template_path(self)
        init_window(self)

    def test_valid_configs(self):
        """Test widgets behavior when a valid config type is loaded."""
        self.ct_mock.side_effect = get_template
        self.cb.setCurrentText('Type1')

        self.assertTrue(self.rb.isEnabled())
        d = self.tv.model().model_data
        self.assertEqual(d, pvs)

    def test_invalid_config(self):
        """Test widgets behavior when a invalid config type is loaded."""
        self.ct_mock.side_effect = get_template
        self.cb.setCurrentText('Type2')

        self.assertFalse(self.rb.isEnabled())
        d = self.tv.model().model_data
        self.assertEqual(d, list())


class TestReadButton(unittest.TestCase):
    """Test reading a given configuration."""

    def setUp(self):
        """Common method for all test."""
        mock_get_config_template_path(self)
        init_window(self)
        self.cb.setCurrentText('Type1')

    def test_read_config(self):
        """Test reading config."""
        self.rb.click()

        d = self.tv.model().model_data
        self.assertEqual(d, ret_pvs)

    def test_read_config(self):
        """Test reading config."""
        self.rb.click()
        self.assertTrue(self.sb.isEnabled())


class TestSaveButton(unittest.TestCase):
    """Test reading a given configuration."""

    def setUp(self):
        """Common method for all test."""
        mock_get_config_template_path(self)
        init_window(self)
        self.cb.setCurrentText('Type1')
        self.rb.click()

    @mock.patch(path + '.configuration_window.QInputDialog', autospec=True)
    def test_save_config_cancel(self, mock_dlg):
        """Test save config."""
        mock_dlg.getText.return_value = ('', False)
        self.sb.click()
        self.db.insert_config.assert_not_called()

    @mock.patch(path + '.configuration_window.QMessageBox', autospec=True)
    @mock.patch(path + '.configuration_window.QInputDialog', autospec=True)
    def test_save_config_success(self, mock_dlg, mock_msg):
        """Test save config."""
        # Configure mocks
        mock_dlg.getText.return_value = ('Name', True)
        self.db.insert_config.return_value = {'code': 200}
        # Click save button
        self.sb.click()
        # Assertions
        self.assertFalse(self.sb.isEnabled())
        self.db.insert_config.assert_called_once_with(
            'Type1', 'Name', {'pvs': self.tv.model().model_data})
        mock_msg.information.assert_called_once_with(
            self._window, 'Save', 'Saved successfully')


if __name__ == '__main__':
    unittest.main()
