"""Set configuration window."""
import logging
import re

from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, \
    QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QGridLayout

from siriushla.misc.epics.wrapper import PyEpicsWrapper
from siriushla.misc.epics.task import EpicsChecker, EpicsSetter
from siriushla.widgets.windows import SiriusMainWindow
from siriushla.widgets.pvnames_tree import QTreeItem, PVNameTree
from siriushla.widgets.dialog import ReportDialog, ProgressDialog
from siriushla.widgets.load_configuration import LoadConfigurationWidget
# from siriushla.widgets.horizontal_ruler import HorizontalRuler
from siriushla.model import ConfigPVsTypeModel


class SetConfigurationWindow(SiriusMainWindow):
    """Configuration Window to set configration via epics."""

    def __init__(self, db, wrapper=PyEpicsWrapper, parent=None):
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
                min-height: 40em;
            }
            # LoadConfigurationWidget {
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
        self._type_cb.setModel(ConfigPVsTypeModel(self._db, self._type_cb))

        self._splitter = QSplitter(orientation=Qt.Vertical, parent=self)
        self._splitter.setChildrenCollapsible(True)

        # Add table for the configuration name
        self._config_table = LoadConfigurationWidget(self._db)

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
            tree_levels=('sec', 'mag_group', 'device_name'))
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
        self._config_table.configChanged.connect(self._fill_config)
        self._tree.itemChecked.connect(self._item_checked)
        self._set_btn.clicked.connect(self._set)

    @Slot(str)
    def _fill_config_names(self, config_type):
        self._config_table.config_type = config_type

    @Slot(str, str)
    def _fill_config(self, selected, deselected):
        config_type = self._type_cb.currentText()
        config_name = selected
        ret = self._db.get_config(config_type, config_name)
        self._tree.clear()
        self._nr_checked_items = 0
        code = ret['code']
        if code == 200:
            try:
                self._current_config = ret['result']
                pvs = self._current_config['value']['pvs']
                self._tree.items = pvs
                self._tree_msg.setText(
                    'Configuration has {} items'.format(len(pvs)))
                # self._tree.expandAll()
                self._tree.check_all()
                self._tree.expand_all()
            except KeyError:
                self._tree_msg.setText('Configuration has no field pvs')
        else:
            self._tree_msg.setText(
                'Failed to retrieve configuration: error {}'.format(code))
        self._filter_pvs(self._filter_le.text())

    @Slot(str)
    def _filter_pvs(self, text):
        """Filter pvnames based on text inserted at line edit."""
        selected_pvs = 0
        try:
            pattern = re.compile(text, re.I)
        except Exception:  # Ignore malformed patterns?
            pattern = re.compile("malformed")

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

    @Slot(QTreeItem, int, int)
    def _item_checked(self, item, column, value):
        if item.childCount() == 0:
            if value == Qt.Checked:
                self._nr_checked_items += 1
            elif value == Qt.Unchecked:
                self._nr_checked_items -= 1
        self._tree_check_count.setText(
            '{} PVs checked.'.format(self._nr_checked_items))


if __name__ == '__main__':
    import sys
    import siriuspy.envars as _envars
    from siriuspy.servconf.conf_service import ConfigService
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    db = ConfigService(_envars.server_url_configdb)
    w = SetConfigurationWindow(db)
    w.show()

    sys.exit(app.exec_())
