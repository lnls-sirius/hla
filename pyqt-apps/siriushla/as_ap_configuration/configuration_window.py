"""Window used to set and get PV values based on a given configuration."""
import time
import logging
from math import isclose

import epics
from pydm.PyQt.QtCore import QThread, pyqtSignal, pyqtSlot
from pydm.PyQt.QtGui import (QComboBox, QDialog, QLabel, QListWidget,
                             QPushButton, QVBoxLayout, QWidget)

from siriushla.as_ps_cycle.magnets_tree import PVNameTree
from siriushla.as_ps_cycle.progress_dialog import ProgressDialog
from siriushla.widgets.windows import SiriusMainWindow
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName


class EpicsWrapper:
    """"""

    def __init__(self, pv):
        self._pv = epics.get_pv(_VACA_PREFIX + pv)

    @property
    def pvname(self):
        """PV Name."""
        return self._pv.pvname

    def put(self, value):
        """Put if connected."""
        if not self._pv.connected:
            return False
        if self._pv.put(value):
            time.sleep(5e-3)
            return True
        return False

    def check(self, value, wait=2):
        """Do timed get."""
        if not self._pv.connected:
            return False
        t = 0
        init = time.time()
        while t < wait:
            if isinstance(value, float):
                if isclose(self._pv.get(), value, rel_tol=1e-06, abs_tol=0.0):
                    return True
            else:
                if self._pv.get() == value:
                    return True
            t = time.time() - init
            time.sleep(5e-3)
        return False


class EpicsTask(QThread):

    currentItem = pyqtSignal(str)
    itemDone = pyqtSignal()

    def __init__(self, pv_val_list, cls_epics, parent=None):
        super().__init__(parent)
        self._pvs = list()
        self._values = list()
        for pv, val in pv_val_list:
            self._pvs.append(cls_epics(pv))
            self._values.append(val)

        self._quit_task = False

    def size(self):
        """Task Size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to exit thread."""
        return self._quit_task


class EpicsSetter(EpicsTask):

    def run(self):
        """Set magnets to cycling."""
        if self._quit_task:
            self.finished.emit()
        else:
            for i in range(len(self._pvs)):
                self.currentItem.emit(self._pvs[i].pvname)
                self._pvs[i].put(self._values[i])
                self.itemDone.emit()
                if self._quit_task:
                    break
            self.finished.emit()


class EpicsChecker(EpicsTask):

    itemChecked = pyqtSignal(str, bool)

    def run(self):
        if self._quit_task:
            self.finished.emit()
        else:
            for i in range(len(self._pvs)):
                pv, val = self._pvs[i], self._values[i]
                self.currentItem.emit(pv.pvname)
                equal = pv.check(val)
                self.itemDone.emit()
                self.itemChecked.emit(pv.pvname, equal)
                if self._quit_task:
                    break
            self.finished.emit()


class ReportDialog(QDialog):
    """Report failed items."""

    def __init__(self, items, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._items = items
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.items_list = QListWidget(self)
        self.items_list.addItems(self._items)
        self.ok_btn = QPushButton('Ok', self)

        self.layout.addWidget(self.items_list)
        self.layout.addWidget(self.ok_btn)

        self.ok_btn.clicked.connect(self.accept)


class ConfigurationWindow(SiriusMainWindow):
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

    def _setup_ui(self):
        # Set central widget
        self._central_widget = QWidget()
        self._central_widget.layout = QVBoxLayout()
        self._central_widget.setLayout(self._central_widget.layout)
        self.setCentralWidget(self._central_widget)

        # Add combo box with types
        self._type_cb = QComboBox(self)
        self._type_cb.setObjectName('type_cb')
        ret = self._db.get_types()
        if ret['code'] == 200:
            self._type_cb.addItem('Select a configuration type...')
            self._type_cb.addItems(ret['result'])
        else:
            self._type_cb.addItem(self._conn_fail_msg)

        # Add combo box for the configuration name
        self._config_cb = QComboBox(self)
        self._config_cb.setObjectName('name_cb')
        self._config_cb.setDisabled(True)

        # Add Selection Tree
        self._tree_msg = QLabel(self)
        self._tree_msg.setObjectName('tree_msg')
        self._tree = PVNameTree(
            tree_levels=('sec', '_device_type', 'device_name'))
        self._tree.setColumnCount(2)
        self._tree.setObjectName('tree')

        # Add Send Button
        self._set_btn = QPushButton('Set', self)
        self._set_btn.setObjectName('set_btn')

        # Add widgets
        self._central_widget.layout.addWidget(self._type_cb)
        self._central_widget.layout.addWidget(self._config_cb)
        self._central_widget.layout.addWidget(self._tree_msg)
        self._central_widget.layout.addWidget(self._tree)
        self._central_widget.layout.addWidget(self._set_btn)

        # Add signals
        self._type_cb.currentTextChanged.connect(self._fill_config_names)
        self._config_cb.currentIndexChanged.connect(self._fill_config)
        self._set_btn.clicked.connect(self._set)

    @pyqtSlot(str)
    def _fill_config_names(self, config_type):
        ret = self._db.get_names_by_type(config_type)
        self._config_cb.clear()
        if ret['code'] == 200:
            self._config_cb.setEnabled(True)
            if ret['result']:
                self._config_cb.addItem('Select a configuration...')
                self._config_cb.addItems(ret['result'])
            else:
                self._config_cb.addItem('No configurations found...')
        else:
            self._config_cb.setEnabled(True)
            self._config_cb.addItem(self._conn_fail_msg)

    @pyqtSlot(int)
    def _fill_config(self, config_idx):
        if config_idx <= 0:
            return
        config_type = self._type_cb.currentText()
        config_name = self._config_cb.currentText()
        ret = self._db.get_config(config_type, config_name)
        self._tree.clear()
        code = ret['code']
        if code == 200:
            try:
                self._current_config = ret['result']
                # pvs = [SiriusPVName(pv[0])
                #        for pv in ret['result']['value']['pvs']]
                pvs = self._current_config['value']['pvs']
                self._tree.items = pvs
                self._tree_msg.setText(
                    'Configuration has {} items'.format(len(pvs)))
            except KeyError:
                self._tree_msg.setText('Configuration has no field pvs')
        else:
            self._tree_msg.setText(
                'Failed to retrieve configuration: error {}'.format(code))

    @pyqtSlot()
    def _set(self):
        # Get selected PVs
        sel_pvs = self._tree.checked_items()
        # Get PVs values
        pvs_val = [pv_val for pv_val in self._current_config['value']['pvs']
                   if pv_val[0] in sel_pvs]
        # Get PVs RB
        pvs_rb_val = list()
        for pv_val in pvs_val:
            pv_rb_val = list(pv_val)
            if pv_rb_val[0].endswith('-Cmd'):
                continue
            pv_rb_val[0] = \
                pv_rb_val[0].replace('-Sel', '-Sts').replace('-SP', '-RB')
            pvs_rb_val.append((pv_rb_val))
        # Create threads
        failed_items = []
        set_task = EpicsSetter(pvs_val, self._wrapper, self)
        check_task = EpicsChecker(pvs_rb_val, self._wrapper, self)
        check_task.itemChecked.connect(
            lambda pv, status: failed_items.append(pv) if not status else None)
        # Set/Check PVs values and show wait dialog informing user
        labels = ['Setting PV values', 'Checking PV values']
        tasks = [set_task, check_task]
        self.logger.info(
            'Setting {} configuration'.format(self._current_config['name']))
        dlg = ProgressDialog(labels, tasks, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return
        # Show report dialog informing user results
        # print(failed_items)
        for item in failed_items:
            self.logger.info('Failed to set/check {}'.format(item))
        self._report = ReportDialog(failed_items, self)
        self._report.show()


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriuspy.servconf.conf_service import ConfigService

    app = SiriusApplication()
    db = ConfigService('http://10.0.7.55:8085')
    w = ConfigurationWindow(db)
    w.show()

    t_cb = w.findChild(QComboBox, 'type_cb')
    n_cb = w.findChild(QComboBox, 'name_cb')

    t_cb.setCurrentText('temp')
    n_cb.setCurrentText('turn_botstb_on')

    sys.exit(app.exec_())
