"""Load Configuration Widget."""
import re

from qtpy.QtCore import Qt, Signal, Slot, QItemSelection
from qtpy.QtWidgets import QWidget, QLineEdit, QTableView, QVBoxLayout, \
    QHeaderView

from siriushla.model import ConfigDbTableModel


class LoadConfigurationWidget(QWidget):
    """Widget that loads a configuration."""

    NAME_COL = None
    CONFIG_TYPE_COL = None

    configChanged = Signal(str, str)
    connectionError = Signal(int, str, str)

    def __init__(self, connection, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._connection = connection
        self._setup_ui()
        self.config_type = ''
        self._table.model().connectionError.connect(self.connectionError)

    def _setup_ui(self):
        self._filter_le = QLineEdit(self)
        self._filter_le.setPlaceholderText("Search for configurations...")
        self._filter_le.textChanged.connect(self._filter_rows)

        self._table = QTableView(self)
        self._table.setModel(
            ConfigDbTableModel('',  self._connection))
        self._table.setSelectionBehavior(self._table.SelectRows)
        self._table.setSelectionMode(self._table.SingleSelection)
        self._table.setSortingEnabled(True)
        # self._table.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self._table.hideColumn(0)
        self._table.hideColumn(3)
        self._table.sortByColumn(2, Qt.DescendingOrder)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self._filter_le)
        self.layout.addWidget(self._table)
        self.setLayout(self.layout)

        # Signals
        self._table.selectionModel().selectionChanged.connect(
            self._config_changed)

        # Set constants
        LoadConfigurationWidget.NAME_COL = \
            self._table.model().horizontalHeader.index('name')
        LoadConfigurationWidget.CONFIG_TYPE_COL = \
            self._table.model().horizontalHeader.index('config_type')

    @property
    def config_type(self):
        """selected_configConfiguration type name."""
        return self._config_type

    @config_type.setter
    def config_type(self, name):
        self._config_type = name
        self._table.model().config_type = self._config_type
        self._table.sortByColumn(2, Qt.DescendingOrder)

    @property
    def config_name(self):
        """Return selected configuration name."""
        indexes = self._table.selectionModel().selectedIndexes()
        if indexes:
            return indexes[1].data()
        return None

    @Slot(str)
    def _filter_rows(self, text):
        """Filter power supply widgets based on text inserted at line edit."""
        try:
            pattern = re.compile(text, re.I)
        except Exception:  # Ignore malformed patterns?
            pattern = re.compile("malformed")

        i = 0
        for idx in range(self._table.model().rowCount(1)):
            name = self._table.model().createIndex(idx, self.NAME_COL).data()
            if not pattern.search(name):
                self._table.hideRow(idx)
            else:
                self._table.showRow(idx)
                i += 1
        # self.nr_configs.setText(str(i))

    @Slot(QItemSelection, QItemSelection)
    def _config_changed(self, selected, deselected):
        selected_config = self._table.model().data(selected.indexes()[1])
        if deselected:
            deselected_config = \
                self._table.model().data(deselected.indexes()[1])
        else:
            deselected_config = ''
        self.configChanged.emit(selected_config, deselected_config)

    def resizeEvent(self, event):
        """Reimplement resize event."""
        width = self._table.width() - self._table.verticalHeader().width()
        self._table.setColumnWidth(1, width*0.65)
        self._table.setColumnWidth(2, width*0.33)
        super().resizeEvent(event)
