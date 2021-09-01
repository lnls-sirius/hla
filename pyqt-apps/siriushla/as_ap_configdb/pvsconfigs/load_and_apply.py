"""Set configuration window."""
import logging

from qtpy.QtCore import Qt, Slot, Signal
from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, \
    QHBoxLayout, QVBoxLayout, QSplitter

import qtawesome as qta

from siriuspy.clientconfigdb import ConfigDBException

from siriushla.common.epics.wrapper import PyEpicsWrapper
from siriushla.common.epics.task import EpicsChecker, EpicsSetter, \
    EpicsConnector, EpicsWait
from siriushla.widgets.windows import SiriusMainWindow
from siriushla.widgets.pvnames_tree import PVNameTree
from siriushla.widgets.dialog import ReportDialog, ProgressDialog
from .. import LoadConfigDialog
from ..models import ConfigPVsTypeModel


class SelectAndApplyPVsWidget(QWidget):
    """Select and Apply PVs widget."""

    settingFinished = Signal()

    def __init__(self, parent, client, wrapper=PyEpicsWrapper):
        super().__init__(parent=parent)
        self._client = client
        self._wrapper = wrapper
        self._current_config = None

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.setupui()

    def setupui(self):
        """Setup widget."""
        # Add Send Button
        self._set_btn = QPushButton('Apply Selected PVs', self)
        self._set_btn.setObjectName('set_btn')
        self._set_btn.setStyleSheet(
            '#set_btn{font-size:1.5em; min-width:8em;}')
        self._set_btn.clicked.connect(self._set)

        # Add Selection Tree
        self._tree = PVNameTree(
            tree_levels=('sec', 'dis', 'dev', 'device_name'))
        self._tree.updateItemCheckedCount.connect(
            self._update_but_text)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel('<h3>Configuration</h3>'))
        self.layout().addWidget(self._tree)
        hlay = QHBoxLayout()
        hlay.addStretch()
        hlay.addWidget(self._set_btn)
        hlay.addStretch()
        self.layout().addLayout(hlay)

    @property
    def current_config_type(self):
        """Current config type."""
        if self.current_config:
            return self.current_config['config_type']
        return None

    @property
    def current_config(self):
        """Current config data."""
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

        for data in self._current_config['value']['pvs']:
            try:
                pvo, value, delay = data
            except ValueError:
                pvo, value = data
                delay = 1e-2
            if pvo in selected_pvs:
                set_pvs_tuple.append((pvo, value, delay))
                if pvo.endswith('-Cmd'):
                    self.logger.warning('{} being checked'.format(pvo))
                check_pvs_tuple.append((pvo, value, delay))

        # Create thread
        failed_items = []
        pvs, values, delays = zip(*set_pvs_tuple)
        conn_task = EpicsConnector(pvs, self._wrapper, self)
        set_task = EpicsSetter(pvs, values, delays, self._wrapper, self)
        pvs, values, delays = zip(*check_pvs_tuple)
        check_task = EpicsChecker(pvs, values, delays, self._wrapper, self)
        check_task.itemChecked.connect(
            lambda pv, status: failed_items.append(pv) if not status else None)

        sleep_task = EpicsWait(pvs, wait_time=2.0, parent=self)

        # Set/Check PVs values and show wait dialog informing user
        labels = [
            'Connecting with PVs',
            'Setting PV values',
            'Waiting IOCs updates',
            'Checking PV values']
        tasks = [conn_task, set_task, sleep_task, check_task]
        self.logger.debug(
            'Setting {} configuration'.format(self._current_config['name']))
        dlg = ProgressDialog(labels, tasks, self)
        dlg.rejected.connect(set_task.exit_task)
        dlg.rejected.connect(check_task.exit_task)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return
        # Show report dialog informing user results
        for item in failed_items:
            self.logger.warning('Failed to set/check {}'.format(item))
        self._report = ReportDialog(failed_items, self)
        self._report.exec_()
        self.settingFinished.emit()

    @Slot(str, str)
    def fill_config(self, config_type, config_name):
        """Fill config data."""
        self._tree.clear()
        try:
            ret = self._client.get_config_info(
                config_name, config_type=config_type)
            ret['value'] = self._client.get_config_value(
                config_name, config_type=config_type)
            self._current_config = ret
            pvs = self._current_config['value']['pvs']
            self._tree.items = pvs
            self._tree.check_all()
            self._tree.collapse_all()
        except KeyError:
            self._tree.message = 'Configuration has no field pvs'
        except ConfigDBException as err:
            self._tree.message = 'Failed to retrieve configuration:' + \
                ' error {}'.format(err.server_code)

    @Slot(int)
    def _update_but_text(self, count):
        """Update apply button text."""
        text = 'Apply Selected PVs ({})'.format(count) \
            if count else 'Apply Selected PVs'
        self._set_btn.setText(text)


class SelectConfigWidget(QWidget):
    """Select config Widget."""

    configChanged = Signal(str, str)

    def __init__(self, parent, client):
        super().__init__(parent=parent)
        self._client = client
        self.setupui()

    def setupui(self):
        """Setup widget."""
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
        hlay = QHBoxLayout()
        hlay.setContentsMargins(9, 9, 18, 9)
        hlay.addWidget(self._type_cb)
        hlay.addWidget(self._reload_btn)
        self._config_type_widget.layout().addLayout(hlay)

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
        """Current config type."""
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
