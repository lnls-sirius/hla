import logging

from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QDialog, \
    QWidget, QFrame, QLabel, QPushButton, QMessageBox, QHeaderView, \
    QTableView
from qtpy.QtCore import Slot, Signal

from siriuspy.servconf.conf_service import ConfigService
from siriushla.as_ap_servconf.config_server import ConfigDbTableModel


class LoadConfiguration(QDialog):
    """."""
    data = Signal(str)

    NAME_COL = None
    CONFIG_TYPE_COL = None

    def __init__(self, config_type, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._model = ConfigService()
        self._config_type = config_type
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.setupui()
        self.setWindowTitle("Configuration Manager")

    def setupui(self):
        self.setGeometry(500, 500, 800, 400)
        self.layoutv = QVBoxLayout(self)

        # Basic widgets
        self.editor = QTableView()
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.pressed.connect(self.close)
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

        # Header widget
        self.header = QFrame(self)
        self.header.setObjectName('Header')
        self.header.layout = QHBoxLayout(self.header)
        self.header.layout.addStretch()
        self.header.layout.addWidget(
            QLabel('Configuration Database Manager', self.header))
        self.header.layout.addStretch()

        # Sub header with database genral information
        self.sub_header = QFrame(self)
        self.sub_header.layout = QVBoxLayout(self.sub_header)

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel('<b>Server:</b>', self.sub_header))
        hbl.addWidget(QLabel(self._model.url, self.sub_header))
        hbl.addStretch()
        self.sub_header.layout.addLayout(hbl)

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel('<b>DB Size:</b>', self.sub_header))
        request = self._model.query_db_size()
        if request['code'] == 200:
            dbsize = '{:.2f} MB'.format(request['result']['size']/(1024*1024))
        else:
            dbsize = 'Failed to retrieve information'
        hbl.addWidget(QLabel(dbsize, self.sub_header))
        hbl.addStretch()
        self.sub_header.layout.addLayout(hbl)

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel(
            '<b>Configuration Type:</b>', self.sub_header))
        hbl.addWidget(QLabel(self._config_type, self.sub_header))
        hbl.addStretch()
        self.sub_header.layout.addLayout(hbl)

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel(
            '<b>Number of Configurations:</b>', self.sub_header))
        nr_configs = QLabel(self)
        request = self._model.find_nr_configs(config_type=self._config_type)
        if request['code'] == 200:
            nr_configs.setText(str(request['result']))
        hbl.addStretch()
        self.sub_header.layout.addLayout(hbl)

        # Main widget layout setup
        self.layoutv.addWidget(self.header)
        self.layoutv.addWidget(self.sub_header)
        self.layoutv.addWidget(self.config_viewer)

        # Set table models and options
        self.editor_model = ConfigDbTableModel(self._config_type, self._model)
        self.editor.setModel(self.editor_model)
        self.editor.setSelectionBehavior(self.editor.SelectRows)
        self.editor.setSortingEnabled(True)
        self.editor.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        # Fill tree when a configuration is selected
        self.editor.selectionModel().selectionChanged.connect(self._fill_tree)
        # Connect database error to slot that show messages
        self.editor_model.connectionError.connect(self._database_error)
        # Set constants
        LoadConfiguration.NAME_COL = \
            self.editor_model.horizontalHeader.index('name')
        LoadConfiguration.CONFIG_TYPE_COL = \
            self.editor_model.horizontalHeader.index('config_type')

        self.editor.resizeColumnsToContents()

    @Slot()
    def _fill_tree(self, *args):
        rows = self._get_selected_rows(self.editor)
        # Set tree data
        if rows:
            config = self._type_name(rows.pop(), self.editor_model)
            self.load_button.setEnabled(True)
            self.load_button.setText('Load {}'.format(config[1]))
        else:
            self.load_button.setEnabled(False)
        self.load_button.style().polish(self.load_button)

    @Slot()
    def _load_configuration(self):
        # self.editor.selectRow(index.row())
        rows = list(self._get_selected_rows(self.editor))
        config = self._type_name(rows.pop(), self.editor_model)
        self.data.emit(config[1])
        self.accept()

    @Slot(int, str, str)
    def _database_error(self, code, message, operation):
        tpe = QMessageBox.Warning
        title = 'Something went wrong'
        msg = '{}: {}, while trying to {}'.format(code, message, operation)
        QMessageBox(tpe, title, msg).exec_()

    def _get_selected_rows(self, table):
        index_list = table.selectionModel().selectedIndexes()
        return {idx.row() for idx in index_list}

    def _type_name(self, row, model):
        # Return config_type and name given a row and a table model
        return (model.createIndex(row, self.CONFIG_TYPE_COL).data(),
                model.createIndex(row, self.NAME_COL).data())


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication
    def test(a):
        print(a)
    app = SiriusApplication()
    win = LoadConfiguration('bo_normalized')
    win.data.connect(test)
    win.show()
    sys.exit(app.exec_())
