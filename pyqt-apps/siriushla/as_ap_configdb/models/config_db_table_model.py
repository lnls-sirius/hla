"""Configuration database model."""
import time

from qtpy.QtCore import Qt, Signal, QAbstractTableModel, \
    QAbstractItemModel, QModelIndex
from qtpy.QtWidgets import QMessageBox

from siriuspy.clientconfigdb import ConfigDBException


class ConfigDbTableModel(QAbstractTableModel):
    """Model for configuration database."""

    removeRow = Signal(QModelIndex)
    connectionError = Signal(int, str, str)
    horizontalHeader = ('config_type', 'name', 'created', 'modified')

    def __init__(self, config_type, client, discarded=False, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._client = client
        self._discarded = discarded
        self._config_type = config_type
        self.setupModelData(config_type)

    @property
    def config_type(self):
        """Configuration type name."""
        return self._config_type

    @config_type.setter
    def config_type(self, value):
        self._config_type = value
        self.setupModelData(self._config_type)

    def rowCount(self, index):
        """Return number of configurations."""
        return len(self._configs)

    def columnCount(self, index):
        """Return number of columns."""
        return len(self.horizontalHeader)

    def data(self, index, role=Qt.DisplayRole):
        """Return data at index."""
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        columnName = self.horizontalHeader[index.column()]
        if columnName in ('config_type', 'name'):
            return self._configs[index.row()][columnName]
        elif columnName == 'created':
            tmstmp = self._configs[index.row()][columnName]
            return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(tmstmp))
        elif columnName == 'modified':
            tmstmp = self._configs[index.row()][columnName][-1]
            return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(tmstmp))
        else:
            return str(self._configs[index.row()][columnName])

        return None

    def headerData(self, section, orientation, role):
        """Return header."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.horizontalHeader[section]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1

        return None

    def setupModelData(self, config_type, discarded=False):
        """Set model data."""
        self.beginResetModel()
        try:
            self._configs = self._client.find_configs(
                config_type=config_type, discarded=self._discarded)
        except ConfigDBException as err:
            self._configs = []
            QMessageBox.warning(self.parent(), 'Error', str(err))
        self.endResetModel()

    def sort(self, column, order=Qt.AscendingOrder):
        """Sort model by column."""
        col = self.horizontalHeader[column]
        reverse = False if order == Qt.AscendingOrder else True
        self.beginResetModel()
        if col in ('config_type', 'name'):
            self._configs.sort(key=lambda x: x[col].lower(), reverse=reverse)
        elif col == 'modified':
            self._configs.sort(key=lambda x: len(x[col]), reverse=reverse)
        else:
            self._configs.sort(key=lambda x: x[col], reverse=reverse)
        self.endResetModel()

    def flags(self, index):
        """Override to make cells editable."""
        if not index.isValid():
            return Qt.ItemIsEnabled
        return QAbstractItemModel.flags(self, index)

    def removeRows(self, row, count=1, index=QModelIndex()):
        """Updated table."""
        self.beginRemoveRows(index, row, row + count - 1)
        config = self._configs[row]
        if not self._discarded:
            try:
                request = self._client.delete_config(
                    config['name'], config_type=config['config_type'])
            except ConfigDBException as err:
                self.connectionError.emit(
                    err.server_code, err.server_message,
                    'delete configuration')
                return False
        else:
            try:
                request = self._client.retrieve_config(
                    config['name'], config_type=config['config_type'])
            except ConfigDBException as err:
                self.connectionError.emit(
                    err.server_code, err.server_message,
                    'retrieve configuration')
        self._configs = self._configs[:row] + self._configs[row + count:]
        self.endRemoveRows()
        return True
