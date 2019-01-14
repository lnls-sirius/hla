"""Window used to set and get PV values based on a given configuration."""
import logging
import re
import time
from math import isclose

import epics
from numpy import ndarray
from qtpy.QtCore import Slot, QSize
from qtpy.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QInputDialog,
                            QLabel, QLineEdit, QListWidget, QMessageBox,
                            QPushButton, QSizePolicy, QTableView, QVBoxLayout,
                            QWidget)

from siriushla.as_ap_pvsconfmgr import (ConfigNamesModel, ConfigTypeModel,
                                        EpicsChecker, EpicsGetter, EpicsSetter,
                                        PVConfigurationTableModel)
from siriushla.as_ps_cycle.progress_dialog import ProgressDialog
from siriushla.widgets.pvnames_tree import PVNameTree
from siriushla.widgets.windows import SiriusMainWindow
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName


class EpicsWrapper:
    """Wraps a PV object.

    Implements:
    pvname
    connected
    put
    check
    get
    """

    def __init__(self, pv):
        """Create PV object."""
        self._pv = epics.get_pv(_VACA_PREFIX + pv)

    @property
    def pvname(self):
        """PV Name."""
        return self._pv.pvname

    def connected(self, pv, wait=50e-3):
        """Wait pv connection."""
        t = 0
        init = time.time()
        while not pv.connected:
            t = time.time() - init
            if t > wait:
                return False
            time.sleep(5e-3)
        return True

    def put(self, value):
        """Put if connected."""
        if not self.connected(self._pv):
            return False

        if self._pv.put(value):
            time.sleep(50e-3)
            return True
        return False

    def check(self, value, wait=5):
        """Do timed get."""
        if not self.connected(self._pv):
            return False

        t = 0
        init = time.time()
        while t < wait:
            if isinstance(value, float):
                pv_value = self._pv.get(use_monitor=False)
                if pv_value is not None and isclose(pv_value, value, rel_tol=1e-06, abs_tol=0.0):
                    return True
            else:
                if self._pv.get() == value:
                    return True
            t = time.time() - init
            time.sleep(5e-3)

        return False

    def get(self):
        """Return PV value."""
        return self._pv.get(timeout=0.5)


class ReportDialog(QDialog):
    """Report list of items."""

    def __init__(self, items, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._items = items
        self._setup_ui()
        self.setWindowTitle('Report')

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        if self._items:
            self.header = QLabel('Failed PVs', self)
            self.layout.addWidget(self.header)
            self.items_list = QListWidget(self)
            self.items_list.addItems(self._items)
            self.layout.addWidget(self.items_list)
            self.setMinimumSize(QSize(600, 300))
        else:
            self.header = QLabel('Done', self)
            self.layout.addWidget(self.header)
            self.setMinimumSize(QSize(300, 100))
        self.ok_btn = QPushButton('Ok', self)
        self.layout.addWidget(self.ok_btn)

        self.ok_btn.clicked.connect(self.accept)


class SetConfigurationWindow(SiriusMainWindow):
    """Configuration Window."""

    def __init__(self, db, wrapper=EpicsWrapper, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._db = db
        self._wrapper = wrapper

        self._conn_fail_msg = 'Could not connect to {}'.format(self._db.url)

        self._current_config = None

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self._setup_ui()
        self._central_widget.setStyleSheet("""
            #CentralWidget {
                min-width: 40em;
                max-width: 40em;
                min-height: 40em;
                max-height: 40em;
            }
        """)
        self.setWindowTitle('Set saved configuration')

    def _setup_ui(self):
        # Set central widget
        self._central_widget = QWidget()
        self._central_widget.setObjectName('CentralWidget')
        self._central_widget.layout = QHBoxLayout()
        self._central_widget.setLayout(self._central_widget.layout)
        self.setCentralWidget(self._central_widget)

        self._set_widget = QWidget()
        self._set_widget.layout = QVBoxLayout()
        self._set_widget.setLayout(self._set_widget.layout)

        self._central_widget.layout.addWidget(self._set_widget)

        # Add combo box with types
        self._type_cb = QComboBox(self)
        self._type_cb.setObjectName('type_cb')
        self._type_cb.setModel(ConfigTypeModel(self._db, self._type_cb))

        # Add combo box for the configuration name
        self._config_cb = QComboBox(self)
        self._config_cb.setObjectName('name_cb')
        self._config_cb.setModel(ConfigNamesModel(self._db, self._config_cb))

        # Add Selection Tree
        self._tree_msg = QLabel(self)
        self._tree_msg.setObjectName('tree_msg')
        self._tree = PVNameTree(
            tree_levels=('sec', 'mag_group', 'device_name'))
        self._tree.setColumnCount(2)
        self._tree.setObjectName('tree')

        # Add Send Button
        self._set_btn = QPushButton('Set', self)
        self._set_btn.setObjectName('set_btn')

        # Add widgets
        self._set_widget.layout.addWidget(self._type_cb)
        self._set_widget.layout.addWidget(self._config_cb)
        self._set_widget.layout.addWidget(self._tree_msg)
        self._set_widget.layout.addWidget(self._tree)
        self._set_widget.layout.addWidget(self._set_btn)

        # Add signals
        self._type_cb.currentTextChanged.connect(self._fill_config_names)
        self._config_cb.currentIndexChanged.connect(self._fill_config)
        self._set_btn.clicked.connect(self._set)

    @Slot(str)
    def _fill_config_names(self, config_type):
        self._config_cb.model().config_type = config_type
        self._config_cb.setCurrentIndex(0)
        self._tree.items = ()
        self._tree_msg.setText('Select a configuration')

    @Slot(int)
    def _fill_config(self, config_idx):
        if config_idx <= 0:
            self._tree_msg.setText('Select a configuration')
            return
        config_type = self._type_cb.currentText()
        config_name = self._config_cb.currentText()
        ret = self._db.get_config(config_type, config_name)
        self._tree.clear()
        code = ret['code']
        if code == 200:
            try:
                self._current_config = ret['result']
                pvs = self._current_config['value']['pvs']
                self._tree.items = pvs
                self._tree_msg.setText(
                    'Configuration has {} items'.format(len(pvs)))
                self._tree.expandAll()
            except KeyError:
                self._tree_msg.setText('Configuration has no field pvs')
        else:
            self._tree_msg.setText(
                'Failed to retrieve configuration: error {}'.format(code))

    @Slot()
    def _set(self):
        # Get selected PVs
        sel_pvs = self._tree.checked_items()
        # Get PVs values
        pvs_val = {pv_val[0]: pv_val[1] 
                   for pv_val in self._current_config['value']['pvs']
                   if pv_val[0] in sel_pvs}
        # Get PVs RB
        pvs_rb_val = dict()
        for pv, val in pvs_val.items():
            # pv_rb_val = list(pv_val)
            if pv.endswith('-Cmd'):
                continue
            pv_rb = \
                pv.replace('-Sel', '-Sts').replace('-SP', '-RB')
            pvs_rb_val[pv_rb] = val
        # Create thread
        failed_items = []
        set_task = EpicsSetter(list(pvs_val), self._wrapper,
                               list(pvs_val.values()), self)
        check_task = EpicsChecker(list(pvs_rb_val), self._wrapper,
                                  list(pvs_rb_val.values()), self)
        check_task.itemChecked.connect(
            lambda pv, status: failed_items.append(pv) if not status else None)
        # Set/Check PVs values and show wait dialog informing user
        labels = ['Setting PV values', 'Checking PV values']
        tasks = [set_task, check_task]
        self.logger.info(
            'Setting {} configuration'.format(self._current_config['name']))
        dlg = ProgressDialog(labels, tasks, self)
        dlg.rejected.connect(set_task.exit_task)
        dlg.rejected.connect(check_task.exit_task)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return
        # Show report dialog informing user results
        for item in failed_items:
            self.logger.warn('Failed to set/check {}'.format(item))
        self._report = ReportDialog(failed_items, self)
        self._report.show()


class ReadConfigurationWindow(SiriusMainWindow):
    """Read configuration window."""

    def __init__(self, db, wrapper=EpicsWrapper, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._db = db
        self._wrapper = wrapper

        self._current_config = None
        self._valid_config = False

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self._setup_ui()
        self._central_widget.setStyleSheet("""
            #CentralWidget {
                min-width: 40em;
                max-width: 40em;
                min-height: 40em;
                max-height: 40em;
            }
        """)
        self.setWindowTitle('Create new configuration')

    def _setup_ui(self):
        # Set central widget
        self._central_widget = QWidget()
        self._central_widget.setObjectName('CentralWidget')
        self._central_widget.layout = QVBoxLayout()
        self._central_widget.setLayout(self._central_widget.layout)
        self.setCentralWidget(self._central_widget)

        # Add combo box with types
        self._type_cb = QComboBox(self)
        self._type_cb.setObjectName('type_cb')
        self._type_cb.setModel(ConfigTypeModel(self._db, self._type_cb))

        # Add LineEdit for configuration name
        # self._name_le = QLineEdit(self)
        # self._name_le.setObjectName('name_le')

        # Add configuration table
        self._table = QTableView(self)
        self._table.setObjectName('config_tbl')
        self._table.setModel(PVConfigurationTableModel())

        # Add Read Button
        self._read_btn = QPushButton('Read', self)
        self._read_btn.setObjectName('read_btn')
        self._read_btn.setEnabled(False)

        # Add Save Button
        self._save_btn = QPushButton('Save', self)
        self._save_btn.setObjectName('save_btn')
        self._save_btn.setEnabled(False)

        # Add widgets
        self._central_widget.layout.addWidget(self._type_cb)
        # self._central_widget.layout.addWidget(self._name_le)
        self._central_widget.layout.addWidget(self._read_btn)
        self._central_widget.layout.addWidget(self._table)
        self._central_widget.layout.addWidget(self._save_btn)

        # Add signals
        self._type_cb.currentTextChanged.connect(self._fill_table)
        self._read_btn.clicked.connect(self._read)
        self._save_btn.clicked.connect(self._save)

    @Slot(str)
    def _fill_table(self, config_type):
        self._table.model().config_type = config_type
        self._table.resizeColumnsToContents()
        self._is_configuration_valid()

    @Slot()
    def _read(self):
        failed_items = []
        tbl_data = self._table.model().model_data
        # Get PVs
        vp = _VACA_PREFIX
        pvs = {tbl_data[i][0]: i for i in range(len(tbl_data))}
        # Create thread to read PVs
        task = EpicsGetter(list(pvs), self._wrapper, parent=self)
        task.itemRead.connect(
            lambda pv, value: self._fill_value(pvs[pv.replace(vp, '')], value))
        task.itemNotRead.connect(failed_items.append)
        # Show progress dialog
        dlg = ProgressDialog('Reading PVs...', task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return
        # Show failed items
        for item in failed_items:
            self.logger.warn('Failed to get {}'.format(item))
        self._report = ReportDialog(failed_items, self)
        self._report.show()
        self._table.resizeColumnsToContents()
        if not failed_items:
            self._save_btn.setEnabled(True)

    @Slot()
    def _fill_value(self, row, value):
        self.logger.info('Setting value {} in row {}'.format(value, row))
        index = self._table.model().createIndex(row, 1)
        self._table.model().setData(index, value)

    def _save(self):
        config_type = self._type_cb.currentText()

        success = False
        error = ''
        label = 'Please select a name'
        # Ask for a name until it is either canceled or succesfully inserted
        while not success:
            config_name, status = QInputDialog.getText(
                self, 'Configuration Name', error + label)
            # Check status and configuration name
            if not status:
                success = True
                continue
            if not re.match('^((\w|[()])+([-_/](\w+|[()])])?)+$', config_name):
                self.logger.warning('Name not allowed')
                error = 'Name not allowed<br>'
                continue
            # Get config_type, config_name, data and insert new configuration
            data = self._table.model().model_data
            ret = self._db.insert_config(
                config_type, config_name, {'pvs': data})
            if ret['code'] == 200:  # Worked
                success = True
                self._save_btn.setEnabled(False)
                QMessageBox.information(self, 'Save', 'Saved successfully')
            else:  # Smth went wrong
                code, message = ret['code'], ret['message']
                self.logger.warning('Error {}: {}'.format(code, message))
                if code == 409:
                    error = 'Name already taken'
                else:
                    error = message
                error += '<br/><br/>'

    def _is_configuration_valid(self):
        if self._table.model().model_data:
            self._config_valid = True
        else:
            self._config_valid = False
        self._read_btn.setEnabled(self._config_valid)


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriuspy.servconf.conf_service import ConfigService

    app = SiriusApplication()
    app.setStyleSheet("""
        * {
            font-size: 20pt;
        }
    """)
    db = ConfigService('http://10.0.7.55:8085')
    w1 = SetConfigurationWindow(db)
    w2 = ReadConfigurationWindow(db)
    w1.show()
    w2.show()

    # t_cb = w.findChild(QComboBox, 'type_cb')
    # n_cb = w.findChild(QComboBox, 'name_cb')

    # t_cb.setCurrentText('temp')
    # n_cb.setCurrentText('turn_botstb_on')
    # t_cb.setHidden(True)
    # n_cb.setHidden(True)

    sys.exit(app.exec_())
