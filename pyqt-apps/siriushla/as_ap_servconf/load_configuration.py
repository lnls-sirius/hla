"""Define a window to load configurations."""

import logging
import re
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QTableView, QLineEdit, \
    QWidget, QFrame, QLabel, QPushButton, QMessageBox, QHeaderView
from qtpy.QtCore import Slot, Signal, Qt

from siriuspy.servconf.conf_service import ConfigService
from siriushla.model import ConfigDbTableModel
from siriushla.widgets.windows import SiriusDialog
from siriushla.widgets.load_configuration import LoadConfigurationWidget


class LoadConfiguration(SiriusDialog):
    """Load configurations."""

    configname = Signal(str)

    NAME_COL = None
    CONFIG_TYPE_COL = None

    def __init__(self, config_type, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._model = ConfigService()
        self._config_type = config_type
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._setupui()
        self.setWindowTitle("Configuration Database Manager")

    def _setupui(self):
        self.layoutv = QVBoxLayout(self)

        # Basic widgets
        self.editor = LoadConfigurationWidget(self._model, self)
        self.editor.config_type = self._config_type
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.pressed.connect(self.reject)
        self.load_button = QPushButton('Load', self)
        self.load_button.setEnabled(False)
        self.load_button.pressed.connect(self._load_configuration)

        # Config View Widget
        self.config_viewer = QWidget(self)
        self.config_viewer.layout = QVBoxLayout(self.config_viewer)
        self.config_viewer.layout.addWidget(self.editor)
        hbl = QHBoxLayout()
        hbl.addStretch()
        hbl.addWidget(self.cancel_button)
        hbl.addStretch()
        hbl.addWidget(self.load_button)
        hbl.addStretch()
        self.config_viewer.layout.addLayout(hbl)

        # Sub header with database general information
        self.sub_header = QFrame(self)
        self.sub_header.layout = QHBoxLayout(self.sub_header)
        vbl = QVBoxLayout()
        self.sub_header.layout.addLayout(vbl)

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel('<b>Server:</b>', self.sub_header))
        hbl.addWidget(QLabel(self._model.url, self.sub_header))
        hbl.addStretch()
        vbl.addLayout(hbl)

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel('<b>DB Size:</b>', self.sub_header))
        request = self._model.query_db_size()
        if request['code'] == 200:
            dbsize = '{:.2f} MB'.format(request['result']['size']/(1024*1024))
        else:
            dbsize = 'Failed to retrieve information'
        hbl.addWidget(QLabel(dbsize, self.sub_header))
        hbl.addStretch()
        vbl.addLayout(hbl)

        vbl = QVBoxLayout()
        self.sub_header.layout.addLayout(vbl)
        hbl = QHBoxLayout()
        hbl.addWidget(QLabel(
            '<b>Configuration Type:</b>', self.sub_header))
        hbl.addWidget(QLabel(self._config_type, self.sub_header))
        hbl.addStretch()
        vbl.addLayout(hbl)

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel(
            '<b>Number of Configurations:</b>', self.sub_header))
        self.nr_configs = QLabel(self.sub_header)
        hbl.addWidget(self.nr_configs)
        request = self._model.find_nr_configs(config_type=self._config_type)
        if request['code'] == 200:
            self.nr_configs.setText(str(request['result']))
        hbl.addStretch()
        vbl.addLayout(hbl)


        # # Main widget layout setup
        self.layoutv.addWidget(self.sub_header)
        self.layoutv.addWidget(self.config_viewer)

        # Update Selection when a configuration is selected
        self.editor.configChanged.connect(self._update_selection)
        # Connect database error to slot that show messages
        self.editor.connectionError.connect(self._database_error)

    @Slot(str, str)
    def _update_selection(self, selected, deselected):
        config = selected
        if config:
            self.load_button.setEnabled(True)
            self.load_button.setText('Load {}'.format(config))
        else:
            self.load_button.setEnabled(False)
        self.load_button.style().polish(self.load_button)

    @Slot()
    def _load_configuration(self):
        config = self.editor.config_name
        if config:
            self.configname.emit(config)
        self.accept()

    @Slot(int, str, str)    
    def _database_error(self, code, message, operation):
        tpe = QMessageBox.Warning
        title = 'Something went wrong'
        msg = '{}: {}, while trying to {}'.format(code, message, operation)
        QMessageBox(tpe, title, msg).exec_()


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication

    def test(a):
        """Test."""
        print(a)
    app = SiriusApplication()
    win = LoadConfiguration('bo_normalized')
    win.configname.connect(test)
    win.show()
    sys.exit(app.exec_())
