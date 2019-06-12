"""Load Configuration Widget."""
import re

from qtpy.QtCore import Qt, Signal, Slot, QItemSelection
from qtpy.QtWidgets import QWidget, QLineEdit, QTableView, QVBoxLayout, \
    QLabel, QHBoxLayout, QFrame

from siriuspy.clientconfigdb import ConfigDBException
from .models import ConfigDbTableModel


class ConfigTableWidget(QTableView):
    """Widget that loads a configuration."""

    NAME_COL = ConfigDbTableModel.horizontalHeader.index('name')
    CONFIG_TYPE_COL = ConfigDbTableModel.horizontalHeader.index('config_type')

    configChanged = Signal(str, str)
    connectionError = Signal(int, str, str)

    def __init__(self, client, parent=None, config_type=None):
        """Constructor."""
        super().__init__(parent)
        self._client = client
        self._config_type = config_type or 'not_exist'
        self._setup_ui()

    def _setup_ui(self):
        self.setModel(
            ConfigDbTableModel(self._config_type, self._client))
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        self.setSortingEnabled(True)
        # self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.hideColumn(0)
        self.hideColumn(3)
        self.sortByColumn(2, Qt.DescendingOrder)

        # Signals
        self.selectionModel().selectionChanged.connect(
            self._config_changed)
        self.model().connectionError.connect(self.connectionError)

    @property
    def config_type(self):
        """selected_configConfiguration type name."""
        return self._config_type

    @config_type.setter
    def config_type(self, name):
        self._config_type = name
        self.model().config_type = self._config_type
        self.sortByColumn(2, Qt.DescendingOrder)

    @property
    def config_name(self):
        """Return selected configuration name."""
        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            return indexes[1].data()
        return None

    @Slot(QItemSelection, QItemSelection)
    def _config_changed(self, selected, deselected):
        selected_config = self.model().data(selected.indexes()[1])
        if deselected:
            deselected_config = \
                self.model().data(deselected.indexes()[1])
        else:
            deselected_config = ''
        self.configChanged.emit(selected_config, deselected_config)

    def resizeEvent(self, event):
        """Reimplement resize event."""
        width = self.width() - self.verticalHeader().width()
        self.setColumnWidth(1, width*0.65)
        self.setColumnWidth(2, width*0.33)
        super().resizeEvent(event)


class ConfigDBSearchEngine(QLineEdit):

    NAME_COL = ConfigDbTableModel.horizontalHeader.index('name')
    CONFIG_TYPE_COL = ConfigDbTableModel.horizontalHeader.index('config_type')

    filteredidcs = Signal(list)

    def __init__(self, table, parent=None):
        super().__init__(parent)
        self.table = table
        self.setPlaceholderText(
            'Type the configuration name...')
        self.textChanged.connect(self._filter_rows)

    @Slot(str)
    def _filter_rows(self, text):
        """Filter power supply widgets based on text inserted at line edit."""
        try:
            pattern = re.compile(text, re.I)
        except Exception:  # Ignore malformed patterns?
            return

        idxlist = list()
        for idx in range(self.table.model().rowCount(1)):
            name = self.table.model().createIndex(idx, self.NAME_COL).data()
            if not pattern.search(name):
                self.table.hideRow(idx)
            else:
                self.table.showRow(idx)
                idxlist.append(idx)
        self.filteredidcs.emit(idxlist)


class ConfigDBInfoHeader(QFrame):

    def __init__(self, client, parent=None, config_type=None):
        super().__init__(parent)
        self._client = client
        self._config_type = config_type or 'notexist'
        self.setupui()

    def setupui(self):
        # Sub header with database general information
        self.layout = QHBoxLayout(self)
        vbl = QVBoxLayout()
        self.layout.addLayout(vbl)

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel('<b>Server:</b>', self))
        hbl.addWidget(QLabel(self._client.url, self))
        hbl.addStretch()
        vbl.addLayout(hbl)

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel('<b>DB Size:</b>', self))
        try:
            dbsize = self._client.get_dbsize()
            dbsize = '{:.2f} MB'.format(dbsize/(1024*1024))
        except ConfigDBException:
            dbsize = 'Failed to retrieve information'
        hbl.addWidget(QLabel(dbsize, self))
        hbl.addStretch()
        vbl.addLayout(hbl)

        vbl = QVBoxLayout()
        self.layout.addLayout(vbl)
        hbl = QHBoxLayout()
        hbl.addWidget(QLabel(
            '<b>Configuration Type:</b>', self))
        hbl.addWidget(QLabel(self._config_type, self))
        hbl.addStretch()
        vbl.addLayout(hbl)

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel(
            '<b>Number of Configurations:</b>', self))
        self.nr_configs = QLabel(self)
        hbl.addWidget(self.nr_configs)
        try:
            leng = len(self._client.find_configs(config_type=self._config_type))
        except ConfigDBException:
            leng = 'NA'
        self.nr_configs.setText(str(leng))
        hbl.addStretch()
        vbl.addLayout(hbl)
