"""Set configuration window."""
import logging
import re
import time

from qtpy.QtCore import Qt, Slot, QThread, Signal
from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, \
    QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QGridLayout

import qtawesome as qta

from siriuspy.clientconfigdb import ConfigDBException
from siriushla.common.epics.wrapper import PyEpicsWrapper
from siriushla.common.epics.task import EpicsChecker, EpicsSetter
from siriushla.widgets.windows import SiriusMainWindow
from siriushla.widgets.pvnames_tree import QTreeItem, PVNameTree
from siriushla.widgets.dialog import ReportDialog, ProgressDialog
from .. import LoadConfigDialog
# from siriushla.widgets.horizontal_ruler import HorizontalRuler
from ..models import ConfigPVsTypeModel


class SelectAndApplyPVsWidget(QWidget):

    settingFinished = Signal()

    def __init__(self, parent, client, wrapper=PyEpicsWrapper):
        super().__init__(parent=parent)
        self._client = client
        self._wrapper = wrapper
        self._current_config = None
        self._nr_checked_items = 0

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.setupui()

    def setupui(self):
        # Add Send Button
        self._set_btn = QPushButton('Apply Selected PVs', self)
        self._set_btn.setObjectName('set_btn')
        self._set_btn.setStyleSheet(
            '#set_btn{font-size:1.5em; min-width:8em;}')
        self._set_btn.clicked.connect(self._set)

        self._tree_msg = QLabel(self)
        self._tree_msg.setObjectName('tree_msg')

        # Add Selection Tree
        self._tree_check_count = QLabel(self)
        self._tree_check_count.setObjectName('tree_check_count')
        self._tree = PVNameTree(
            tree_levels=('sec', 'dis', 'dev'))
        self._tree.setColumnCount(3)
        self._tree.setObjectName('tree')
        self._tree.itemChecked.connect(self._item_checked)

        # Add filter for tree
        self._filter_le = QLineEdit(self)
        self._filter_le.setPlaceholderText("Filter PVs...")
        self._filter_le.textChanged.connect(self._filter_pvs)

        self.setLayout(QVBoxLayout())
        hl = QHBoxLayout()
        hl.addWidget(self._tree_msg)
        hl.addWidget(self._tree_check_count)
        self.layout().addWidget(QLabel('<h3>Configuration</h3>'))
        self.layout().addWidget(self._filter_le)
        self.layout().addLayout(hl)
        self.layout().addWidget(self._tree)
        hl = QHBoxLayout()
        hl.addStretch()
        hl.addWidget(self._set_btn)
        hl.addStretch()
        self.layout().addLayout(hl)

    @property
    def current_config_type(self):
        if self.current_config:
            return self.current_config['config_type']

    @property
    def current_config(self):
        return self._current_config['name']

    @current_config.setter
    def current_config(self, value):
        if self._current_config:
            self.fill_config(self._current_config['config_type'], value)

    @Slot()
    def _set(self):
        # Get selected PVs
        selected_pvs = set(self._tree.checked_items())

        set_pvs_tuple = list()
        check_pvs_tuple = list()

        for t in self._current_config['value']['pvs']:
            try:
                pv, value, delay = t
            except ValueError:
                pv, value = t
                delay = 1e-2
            if pv in selected_pvs:
                set_pvs_tuple.append((pv, value, delay))
                if pv.endswith('-Cmd'):
                    self.logger.warning('{} being checked'.format(pv))
                check_pvs_tuple.append((pv, value, delay))

        # Create thread
        failed_items = []
        pvs, values, delays = zip(*set_pvs_tuple)
        set_task = EpicsSetter(pvs, values, delays, self._wrapper, self)
        pvs, values, delays = zip(*check_pvs_tuple)
        check_task = EpicsChecker(pvs, values, delays, self._wrapper, self)
        check_task.itemChecked.connect(
            lambda pv, status: failed_items.append(pv) if not status else None)

        sleep_task = Wait(
            pvs_tuple=check_pvs_tuple, wait_time=2.0,
            fltr='TB-.*:(PS|MA)-(C|Q).*$')

        # Set/Check PVs values and show wait dialog informing user
        labels = ['Setting PV values',
                  'Waiting IOCs updates',
                  'Checking PV values']
        tasks = [set_task, sleep_task, check_task]
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
        self._report.exec_()
        self.settingFinished.emit()

    @Slot(str, str)
    def fill_config(self, config_type, config_name):
        self._tree.clear()
        self._nr_checked_items = 0
        try:
            ret = self._client.get_config_info(
                config_name, config_type=config_type)
            ret['value'] = self._client.get_config_value(
                config_name, config_type=config_type)
            self._current_config = ret
            pvs = self._current_config['value']['pvs']
            self._tree.items = pvs
            self._tree_msg.setText(
                'Configuration has {} items'.format(len(pvs)))
            self._tree.check_all()
            self._tree.collapseAll()
            self._filter_pvs(self._filter_le.text())
        except KeyError:
            self._tree_msg.setText('Configuration has no field pvs')
        except ConfigDBException as err:
            self._tree_msg.setText(
                'Failed to retrieve configuration: error {}'.format(
                    err.server_code))

    @Slot(str)
    def _filter_pvs(self, text):
        """Filter pvnames based on text inserted at line edit."""
        selected_pvs = 0
        try:
            pattern = re.compile(text, re.I)
        except Exception:
            return

        for node in self._tree._leafs:
            if pattern.search(node.data(0, 0)):
                node.setHidden(False)
                selected_pvs += 1
            else:
                # node.setCheckState(0, Qt.Unchecked)
                node.setHidden(True)

        self._tree_msg.setText('Showing {} PVs.'.format(selected_pvs))

    @Slot(QTreeItem, int, int)
    def _item_checked(self, item, column, value):
        if item.childCount() == 0:
            if value == Qt.Checked:
                self._nr_checked_items += 1
            elif value == Qt.Unchecked:
                self._nr_checked_items -= 1
        self._tree_check_count.setText(
            '{} PVs checked.'.format(self._nr_checked_items))


class SelectConfigWidget(QWidget):

    configChanged = Signal(str, str)

    def __init__(self, parent, client):
        super().__init__(parent=parent)
        self._client = client
        self.setupui()

    def setupui(self):
        self.setLayout(QVBoxLayout())

        # Add combo box with types
        self._type_cb = QComboBox(self)
        self._type_cb.setObjectName('type_cb')
        self._type_cb.setModel(ConfigPVsTypeModel(self._client, self._type_cb))
        self._reload_btn = QPushButton(self)
        self._reload_btn.setIcon(qta.icon('fa5s.sync'))
        self._reload_btn.setStyleSheet('max-width: 2em;')

        # Add widgets
        self._config_type_widget = QWidget(self)
        self._config_type_widget.setLayout(QVBoxLayout())
        self._config_type_widget.layout().addWidget(
            QLabel('<h3>Configuration Type</h3>'))
        hl = QHBoxLayout()
        hl.setContentsMargins(9, 9, 18, 9)
        hl.addWidget(self._type_cb)
        hl.addWidget(self._reload_btn)
        self._config_type_widget.layout().addLayout(hl)

        # Add table for the configuration name
        self._config_table = LoadConfigDialog('notexist', self)
        self._config_table.setObjectName('config_table')
        self._config_table.setStyleSheet('#config_table {min-width: 30em;}')
        self._config_table.label_exist.hide()
        self._config_table.sub_header.hide()
        self._config_table.ok_button.hide()
        self._config_table.cancel_button.hide()

        self._config_name_widget = QWidget(self)
        self._config_name_widget.setLayout(QVBoxLayout())
        self._config_name_widget.layout().addWidget(
            QLabel('<h3>Configuration Name</h3>'))
        self._config_name_widget.layout().addWidget(self._config_table)

        self.layout().addWidget(self._config_type_widget)
        self.layout().addWidget(self._config_name_widget)

        # Add signals
        self._type_cb.currentTextChanged.connect(self._fill_config_names)
        self._reload_btn.clicked.connect(self._update_config_names)
        self._config_table.editor.configChanged.connect(self._emit_config)

    @property
    def current_config_type(self):
        return self._type_cb.currentText()

    @current_config_type.setter
    def current_config_type(self, config_type):
        # init with global_config, if it exists
        index = self._type_cb.findText(config_type, Qt.MatchFixedString)
        if index >= 0:
            self._type_cb.setCurrentText(config_type)

    @Slot(str)
    def _fill_config_names(self, config_type):
        self._config_table.editor.config_type = config_type

    @Slot(bool)
    def _update_config_names(self):
        self._config_table.editor.config_type = self._type_cb.currentText()

    @Slot(str, str)
    def _emit_config(self, selected, deselected):
        self.configChanged.emit(self.current_config_type, selected)


class LoadAndApplyConfig2MachineWindow(SiriusMainWindow):
    """Configuration Window to set configration via epics."""

    def __init__(self, client, wrapper=PyEpicsWrapper, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._client = client
        self._wrapper = wrapper

        self._conn_fail_msg = 'Could not connect to {}'.format(
            self._client.url)

        self._setup_ui()
        self.setWindowTitle('Set saved configuration')

        self._load_widget.current_config_type = 'global_config'

    def _setup_ui(self):
        # Set central widget
        self._central_widget = QSplitter(Qt.Horizontal)
        self._central_widget.setObjectName('CentralWidget')
        self.setCentralWidget(self._central_widget)

        self._load_widget = SelectConfigWidget(self, self._client)
        self._set_widget = SelectAndApplyPVsWidget(
            self, self._client, wrapper=self._wrapper)
        self._load_widget.configChanged.connect(self._set_widget.fill_config)
        self._central_widget.addWidget(self._load_widget)
        self._central_widget.addWidget(self._set_widget)


class Wait(QThread):
    """."""

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()
    itemChecked = Signal(str, bool)

    def __init__(self, pvs_tuple, wait_time=1.0, fltr=None, parent=None):
        """."""
        super().__init__(parent)
        self.wait_time = wait_time
        self.pvs_tuple = pvs_tuple
        self._size = 2*len(pvs_tuple) // 20
        self._is_tb_ps = re.compile(fltr)
        self._quit_task = False
        self.sleep_flag = True
        self.check_wait()

    def check_wait(self):
        """."""
        self.sleep_flag = False
        for pvitem in self.pvs_tuple:
            pv, *_ = pvitem
            if self._is_tb_ps.match(pv):
                self.sleep_flag = True
                break

    def size(self):
        """Task Size."""
        return self._size

    def exit_task(self):
        """Set flag to exit thread."""
        self._quit_task = True

    def run(self):
        """."""
        if not self._quit_task:
            t0 = time.time()
            if self.size:
                for i in range(self._size):
                    dt = time.time() - t0
                    self.currentItem.emit(
                        'Waiting for {:3.2f} s...'.format(self.wait_time - dt))
                    time.sleep(self.wait_time/self._size)

                    self.itemDone.emit()
                    self.itemChecked.emit(str(i), True)
            else:
                time.sleep(self.wait_time)
        self.completed.emit()


if __name__ == '__main__':
    import sys
    import siriuspy.envars as _envars
    from siriuspy.clientconfigdb import ConfigDBClient
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    clt = ConfigDBClient(_envars.server_url_configdb)
    w = LoadAndApplyConfig2MachineWindow(clt)
    w.show()

    sys.exit(app.exec_())
