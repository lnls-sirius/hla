"""Set configuration window."""
import logging

from qtpy.QtCore import Slot
from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, \
    QHBoxLayout, QVBoxLayout

from siriushla.misc.epics.wrapper import PyEpicsWrapper
from siriushla.misc.epics.task import EpicsChecker, EpicsSetter
from siriushla.widgets.windows import SiriusMainWindow
from siriushla.widgets.pvnames_tree import PVNameTree
from siriushla.widgets.dialog import ReportDialog, ProgressDialog
from siriushla.as_ap_pvsconfmgr.model import \
    ConfigNamesModel, ConfigTypeModel

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
        selected_pvs = self._tree.checked_items()

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


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriuspy.servconf.conf_service import ConfigService

    app = SiriusApplication()
    db = ConfigService('http://10.0.7.55:8085')
    w = SetConfigurationWindow(db)
    w.show()

    sys.exit(app.exec_())
