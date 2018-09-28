"""Configuration window tests."""
import unittest
from unittest import mock

from qtpy.QtWidgets import QComboBox, QLabel

from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_pvsconfmgr import ConfigurationWindow
from siriushla.widgets.pvnames_tree import PVNameTree

fake_url = 'FakeURL'

db_types_ret = {'code': 200, 'result': ['Type1', 'Type2', 'Type3']}
db_types_fail = {'code': 505}

names_by_type = {'Type1': ['T1C1', 'T1C2', 'T1C3'],
                 'Type2': ['T2C1', 'T2C2'],
                 'Type3': []}
db_names_fail = {'code': 505}

def _db_name_ret(config_type):
    return {'code': 200, 'result': names_by_type[config_type]}

pvs = [('SI-01M1:MA-CH:PwrState-Sel', 1),
       ('SI-01M1:MA-CH:Current-SP', 1.0),
       ('SI-01M1:MA-CH:OpMode-Sel', 1),
       ('SI-02M1:MA-CH:PwrState-Sel', 1),
       ('SI-02M1:MA-CH:Current-SP', 1.0),
       ('SI-02M1:MA-CH:OpMode-Sel', 1),
       ('BO-02:MA-CH:PwrState-Sel', 1),
       ('BO-02:MA-CH:Current-SP', 1.0),
       ('BO-02:MA-CH:OpMode-Sel', 1),
       ('BO-01:MA-QF:PwrState-Sel', 1),
       ('BO-01:MA-QF:Current-SP', 1.0),
       ('BO-01:MA-QF:OpMode-Sel', 1)]
configs = {
    'Type1': {
        'T1C1': {
            'name': 'T1C1',
            'value': {
                'pvs': pvs
            }
        },
        'T1C2': {
            'name': 'T1C2',
            'value': {
                'not_pvs': []
            }
        }
}}

def _db_config_ret(config_type, config_name):
    return {'code': 200, 'result': configs[config_type][config_name]}

conn_fail_msg = 'Could not connect to {}'.format(fake_url)


class TestConfigurationWindow(unittest.TestCase):
    """Test configuration window behaviour."""

    def setUp(self):
        """Test setup."""
        # DB Connection Mock
        self._db = mock.Mock()
        self._db.url = fake_url
        self._db.get_types.return_value = db_types_ret
        # Test object
        self._app = SiriusApplication()
        self._window = ConfigurationWindow(self._db)

    def test_type_cb_setup(self):
        """Test type combo box setup."""
        cb = self._window.findChild(QComboBox, 'type_cb')
        self.assertEqual(cb.currentText(), 'Select a configuration type...')
        self.assertEqual(cb.count(), 4)

    def test_config_cb_setup(self):
        """Test configuration combo box setup."""
        cb = self._window.findChild(QComboBox, 'name_cb')
        self.assertEqual(cb.currentText(), '')
        self.assertFalse(cb.isEnabled())

    def test_tree_setup(self):
        """Test configuration tree setup."""
        tree = self._window.findChild(PVNameTree, 'tree')
        self.assertEqual(tree.items, tuple())


class TestConfigurationTypeSelectionWindow(unittest.TestCase):
    """Test configuration window behaviour."""

    def setUp(self):
        """Test setup."""
        # DB Connection Mock
        self._db = mock.Mock()
        self._db.url = fake_url
        self._db.get_types.return_value = db_types_ret
        # Test object
        self._app = SiriusApplication()
        self._window = ConfigurationWindow(self._db)

    def test_select_type(self):
        """Test selecting a configuration type."""
        # Set names to be returned
        self._db.get_names_by_type.side_effect = _db_name_ret
        t_cb = self._window.findChild(QComboBox, 'type_cb')
        n_cb = self._window.findChild(QComboBox, 'name_cb')
        tree = self._window.findChild(PVNameTree, 'tree')

        t_cb.setCurrentIndex(1)

        self.assertEqual(t_cb.currentText(), 'Type1')
        self.assertEqual(n_cb.currentText(), 'Select a configuration...')
        self.assertEqual(tree.items, tuple())

        t_cb.setCurrentIndex(3)

        self.assertEqual(t_cb.currentText(), 'Type3')
        self.assertEqual(n_cb.currentText(), 'No configurations found...')
        self.assertEqual(tree.items, tuple())

        t_cb.setCurrentIndex(2)

        self.assertEqual(t_cb.currentText(), 'Type2')
        self.assertEqual(n_cb.currentText(), 'Select a configuration...')
        self.assertEqual(tree.items, tuple())

    def test_select_type_fail(self):
        """Test selecting a configuration type."""
        # Set names to be returned
        self._db.get_names_by_type.return_value = db_names_fail
        t_cb = self._window.findChild(QComboBox, 'type_cb')
        n_cb = self._window.findChild(QComboBox, 'name_cb')
        tree = self._window.findChild(PVNameTree, 'tree')

        t_cb.setCurrentIndex(1)

        self.assertEqual(t_cb.currentText(), 'Type1')
        self.assertEqual(n_cb.currentText(), conn_fail_msg)
        self.assertEqual(tree.items, tuple())

        t_cb.setCurrentIndex(3)

        self.assertEqual(t_cb.currentText(), 'Type3')
        self.assertEqual(n_cb.currentText(), conn_fail_msg)
        self.assertEqual(tree.items, tuple())


class TestConfigurationNameSelectionWindow(unittest.TestCase):
    """Test configuration window behaviour."""

    def setUp(self):
        """Test setup."""
        # DB Connection Mock
        self._db = mock.Mock()
        self._db.url = fake_url
        self._db.get_types.return_value = db_types_ret
        self._db.get_names_by_type.side_effect = _db_name_ret
        # Test object
        self._app = SiriusApplication()
        self._window = ConfigurationWindow(self._db)

    def test_select_name(self):
        """Test selection a configuration name."""
        self._db.get_config.side_effect = _db_config_ret
        t_cb = self._window.findChild(QComboBox, 'type_cb')
        n_cb = self._window.findChild(QComboBox, 'name_cb')
        tree = self._window.findChild(PVNameTree, 'tree')
        tree_msg = self._window.findChild(QLabel, 'tree_msg')

        t_cb.setCurrentIndex(1)
        n_cb.setCurrentIndex(1)

        self.assertEqual(tree.items, pvs)
        self.assertEqual(tree_msg.text(), 'Configuration has 12 items')

    def test_select_name_malformed(self):
        """Test selection a malformed configuration name."""
        self._db.get_config.side_effect = _db_config_ret
        t_cb = self._window.findChild(QComboBox, 'type_cb')
        n_cb = self._window.findChild(QComboBox, 'name_cb')
        tree = self._window.findChild(PVNameTree, 'tree')
        tree_msg = self._window.findChild(QLabel, 'tree_msg')

        t_cb.setCurrentIndex(1)
        n_cb.setCurrentIndex(2)

        self.assertEqual(tree.items, tuple())
        self.assertEqual(tree_msg.text(), 'Configuration has no field pvs')

    def test_select_name_server_error(self):
        """Test selection a malformed configuration name."""
        self._db.get_config.side_effect = _db_config_ret
        t_cb = self._window.findChild(QComboBox, 'type_cb')
        n_cb = self._window.findChild(QComboBox, 'name_cb')
        tree = self._window.findChild(PVNameTree, 'tree')
        tree_msg = self._window.findChild(QLabel, 'tree_msg')

        t_cb.setCurrentIndex(1)
        n_cb.setCurrentIndex(1)

        self._db.get_config.side_effect = lambda x, y: {'code': 505}

        n_cb.setCurrentIndex(2)

        self.assertEqual(tree.items, tuple())
        self.assertEqual(tree_msg.text(),
                         'Failed to retrieve configuration: error 505')


class TestConfigurationWindowNoConn(unittest.TestCase):
    """Test configuration window behaviour when connection fails."""

    def setUp(self):
        """Test setup."""
        # DB Connection Mock
        self._db = mock.Mock()
        self._db.url = fake_url
        self._db.get_types.return_value = db_types_fail
        # Test object
        self._app = SiriusApplication()
        self._window = ConfigurationWindow(self._db)

    def test_type_cb_setup(self):
        """Test initial setup."""
        cb = self._window.findChild(QComboBox, 'type_cb')
        self.assertEqual(cb.currentText(), conn_fail_msg)
        self.assertEqual(cb.count(), 1)


class TestConfigurationWindowSetPVs(unittest.TestCase):
    """Test Setting PVs."""

    def setUp(self):
        """Test setup."""
        # DB Connection Mock
        self.db = mock.Mock()
        self.db.url = fake_url
        self.db.get_types.return_value = db_types_ret
        self.db.get_names_by_type.side_effect = _db_name_ret
        self.db.get_config.side_effect = _db_config_ret
        # Epics wrapper Mock
        self.wrapper = mock.Mock()
        self.wrapper_o = self.wrapper.return_value
        self.wrapper_o.pvname = 'FakePVName'
        self.wrapper_o.check.return_value = True
        # Test object
        self.app = SiriusApplication()
        self.window = ConfigurationWindow(self.db, self.wrapper)
        # Widgets
        self.t_cb = self.window.findChild(QComboBox, 'type_cb')
        self.n_cb = self.window.findChild(QComboBox, 'name_cb')
        self.tree = self.window.findChild(PVNameTree, 'tree')
        self.window.show()

    def test_setting_pvs(self):
        self.t_cb.setCurrentIndex(1)
        self.n_cb.setCurrentIndex(1)

        for item in self.tree._leafs:
            item.setCheckState(0, 2)

        calls = []
        for pv, value in pvs:
            calls.append(mock.call(value))

        # Method being tested
        self.window._set_btn.click()

        self.wrapper_o.put.assert_has_calls(calls)
        self.wrapper_o.check.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()
