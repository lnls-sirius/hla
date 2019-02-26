"""Define a window to load configurations."""

import logging
import re
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QTableView, QLineEdit, \
    QWidget, QFrame, QLabel, QPushButton, QMessageBox, QHeaderView
from qtpy.QtCore import Slot, Signal, Qt

from siriuspy.servconf.conf_service import ConfigService
from siriushla.model import ConfigDbTableModel
from siriushla.widgets.windows import SiriusDialog


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
        self.editor = QTableView()
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

        self.search_lineedit = QLineEdit(parent=self)
        self.search_lineedit.setPlaceholderText("Search for configurations...")
        self.search_lineedit.textEdited.connect(self._filter_rows)

        # Main widget layout setup
        self.layoutv.addWidget(self.sub_header)
        self.layoutv.addWidget(self.search_lineedit)
        self.layoutv.addWidget(self.config_viewer)

        # Set table models and options
        self.editor_model = ConfigDbTableModel(self._config_type, self._model)
        self.editor.setModel(self.editor_model)
        self.editor.setSelectionBehavior(self.editor.SelectRows)
        self.editor.setSelectionMode(self.editor.SingleSelection)
        self.editor.setSortingEnabled(True)
        self.editor.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.editor.hideColumn(0)
        self.editor.sortByColumn(2, Qt.DescendingOrder)

        # Update Selection when a configuration is selected
        self.editor.selectionModel().selectionChanged.connect(
            self._update_selection)
        # Connect database error to slot that show messages
        self.editor_model.connectionError.connect(self._database_error)
        # Set constants
        LoadConfiguration.NAME_COL = \
            self.editor_model.horizontalHeader.index('name')
        LoadConfiguration.CONFIG_TYPE_COL = \
            self.editor_model.horizontalHeader.index('config_type')

        self.editor.resizeColumnsToContents()

    @Slot()
    def _update_selection(self, *args):
        config = self._get_config_name()
        if config:
            self.load_button.setEnabled(True)
            self.load_button.setText('Load {}'.format(config))
        else:
            self.load_button.setEnabled(False)
        self.load_button.style().polish(self.load_button)

    @Slot()
    def _load_configuration(self):
        config = self._get_config_name()
        self.configname.emit(config)
        self.accept()

    @Slot(int, str, str)
    def _database_error(self, code, message, operation):
        tpe = QMessageBox.Warning
        title = 'Something went wrong'
        msg = '{}: {}, while trying to {}'.format(code, message, operation)
        QMessageBox(tpe, title, msg).exec_()

    def _get_config_name(self):
        index_list = self.editor.selectionModel().selectedIndexes()
        if index_list:
            row = index_list[0].row()
            return self.editor_model.createIndex(row, self.NAME_COL).data()

    @Slot(str)
    def _filter_rows(self, text):
        """Filter power supply widgets based on text inserted at line edit."""
        try:
            pattern = re.compile(text, re.I)
        except Exception:  # Ignore malformed patterns?
            pattern = re.compile("malformed")

        i = 0
        for idx in range(self.editor_model.rowCount(1)):
            name = self.editor_model.createIndex(idx, self.NAME_COL).data()
            if not pattern.search(name):
                self.editor.hideRow(idx)
            else:
                self.editor.showRow(idx)
                i += 1
        self.nr_configs.setText(str(i))
        # Sroll to top
        # for scroll_area in self.findChildren(QScrollArea):
        #     scroll_area.verticalScrollBar().setValue(0)


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
