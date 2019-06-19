"""Set configuration window."""
import logging
import re
import time

from qtpy.QtCore import Qt, Slot, QThread, Signal
from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, \
    QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QGridLayout

from siriuspy.clientconfigdb import ConfigDBException
from siriushla.misc.epics.wrapper import PyEpicsWrapper
from siriushla.misc.epics.task import EpicsChecker, EpicsSetter
from siriushla.widgets.windows import SiriusMainWindow
from siriushla.widgets.pvnames_tree import QTreeItem, PVNameTree
from siriushla.widgets.dialog import ReportDialog, ProgressDialog
from .. import LoadConfigDialog
# from siriushla.widgets.horizontal_ruler import HorizontalRuler
from ..models import ConfigPVsTypeModel


class LoadAndApplyConfig2MachineWindow(SiriusMainWindow):
    """Configuration Window to set configration via epics."""

    def __init__(self, client, wrapper=PyEpicsWrapper, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._client = client
        self._wrapper = wrapper

        self._conn_fail_msg = 'Could not connect to {}'.format(
            self._client.url)

        self._current_config = None

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self._setup_ui()
        self._central_widget.setStyleSheet("""
            #CentralWidget {
                min-width: 40em;
                min-height: 40em;
            }
            # ConfigTableWidget {
            #     min-height: 10em;
            #     max-height: 10em;
            # }
        """)
        self.setWindowTitle('Set saved configuration')
        self._nr_checked_items = 0

        # init with global_config, if it exists
        index = self._type_cb.findText('global_config', Qt.MatchFixedString)
        if index >= 0:
            self._type_cb.setCurrentText('global_config')

    def _setup_ui(self):
        # Set central widget
        self._central_widget = QWidget()
        self._central_widget.setObjectName('CentralWidget')
        self._central_widget.layout = QHBoxLayout()
        self._central_widget.setLayout(self._central_widget.layout)
        self.setCentralWidget(self._central_widget)

        self._set_widget = QWidget()
        self._set_widget.layout = QGridLayout()
        self._set_widget.setLayout(self._set_widget.layout)
        self._central_widget.layout.addWidget(self._set_widget)

        # Add combo box with types
        self._type_cb = QComboBox(self)
        self._type_cb.setObjectName('type_cb')
        self._type_cb.setModel(ConfigPVsTypeModel(self._client, self._type_cb))

        self._splitter = QSplitter(orientation=Qt.Vertical, parent=self)
        self._splitter.setChildrenCollapsible(True)

        # Add table for the configuration name
        # self._config_table = ConfigTableWidget(self._client)
        self._config_table = LoadConfigDialog('notexist', self)
        self._config_table.label_exist.hide()
        self._config_table.sub_header.hide()
        self._config_table.ok_button.hide()
        self._config_table.cancel_button.hide()

        # Add filter for tree
        self._filter_le = QLineEdit(self)
        self._filter_le.setPlaceholderText("Filter PVs...")
        self._filter_le.textChanged.connect(self._filter_pvs)

        # Add Selection Tree
        self._tree_msg = QLabel(self)
        self._tree_msg.setObjectName('tree_msg')
        self._tree_check_count = QLabel(self)
        self._tree_check_count.setObjectName('tree_check_count')
        self._tree = PVNameTree(
            tree_levels=('sec', 'dis', 'dev'))
        self._tree.setColumnCount(3)
        self._tree.setObjectName('tree')

        # Add Send Button
        self._set_btn = QPushButton('Set', self)
        self._set_btn.setObjectName('set_btn')

        # Add widgets
        self._config_type_widget = QWidget(self)
        self._config_type_widget.setLayout(QVBoxLayout())
        self._config_type_widget.layout().addWidget(
            QLabel('<h3>Configuration Type</h3>'))
        self._config_type_widget.layout().addWidget(self._type_cb)

        self._config_name_widget = QWidget(self)
        self._config_name_widget.setLayout(QVBoxLayout())
        self._config_name_widget.layout().addWidget(
            QLabel('<h3>Configuration Name</h3>'))
        self._config_name_widget.layout().addWidget(self._config_table)

        self._tree_widget = QWidget(self)
        self._tree_label_layout = QHBoxLayout()
        self._tree_label_layout.addWidget(self._tree_msg)
        self._tree_label_layout.addWidget(self._tree_check_count)
        self._tree_widget.layout = QVBoxLayout(self._tree_widget)
        self._tree_widget.layout.addWidget(QLabel('<h3>Configuration</h3>'))
        self._tree_widget.layout.addWidget(self._filter_le)
        self._tree_widget.layout.addLayout(self._tree_label_layout)
        self._tree_widget.layout.addWidget(self._tree)

        self._set_widget.layout.addWidget(self._config_type_widget, 0, 0)
        self._set_widget.layout.addWidget(self._config_name_widget, 1, 0)
        self._set_widget.layout.addWidget(self._tree_widget, 0, 1, 2, 1)
        self._set_widget.layout.addWidget(self._set_btn, 2, 1)

        self._set_widget.layout.setColumnStretch(0, 1)
        self._set_widget.layout.setColumnStretch(1, 1.5)

        # Add signals
        self._type_cb.currentTextChanged.connect(self._fill_config_names)
        self._config_table.editor.configChanged.connect(self._fill_config)
        self._tree.itemChecked.connect(self._item_checked)
        self._set_btn.clicked.connect(self._set)

    @Slot(str)
    def _fill_config_names(self, config_type):
        self._config_table.editor.config_type = config_type

    @Slot(str, str)
    def _fill_config(self, selected, deselected):
        config_type = self._type_cb.currentText()
        config_name = selected
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
            self._tree.expand_all()
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
            filter='TB-.*:(PS|MA)-(C|Q).*$')

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
        self._report.show()

    @Slot(QTreeItem, int, int)
    def _item_checked(self, item, column, value):
        if item.childCount() == 0:
            if value == Qt.Checked:
                self._nr_checked_items += 1
            elif value == Qt.Unchecked:
                self._nr_checked_items -= 1
        self._tree_check_count.setText(
            '{} PVs checked.'.format(self._nr_checked_items))


class Wait(QThread):
    """."""

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()
    itemChecked = Signal(str, bool)

    def __init__(self, pvs_tuple, wait_time=1.0, filter=None, parent=None):
        """."""
        super().__init__(parent)
        self.wait_time = wait_time
        self.pvs_tuple = pvs_tuple
        self._size = 2*len(pvs_tuple) // 20
        self._is_tb_ps = re.compile(filter)
        self._quit_task = False
        self.sleep_flag = True
        self.check_wait()

    def check_wait(self):
        """."""
        self.sleep_flag = False
        for pvitem in self.pvs_tuple:
            pv, value, delay = pvitem
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
        if self._quit_task:
            self.completed.emit()
        else:
            print('Waiting for {} seconds...', self.wait_time)
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
    client = ConfigDBClient(_envars.server_url_configdb)
    w = LoadAndApplyConfig2MachineWindow(client)
    w.show()

    sys.exit(app.exec_())
