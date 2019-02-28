"""Configuration database model."""
import time

from qtpy.QtCore import Qt, Signal, Slot, QAbstractTableModel, \
    QAbstractItemModel, QModelIndex


class ConfigDbTableModel(QAbstractTableModel):
    """Model for configuration database."""

    removeRow = Signal(QModelIndex)
    connectionError = Signal(int, str, str)

    def __init__(self, config_type, connection, discarded=False, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._connection = connection
        self._discarded = discarded
        self.horizontalHeader = \
            ['config_type', 'name', 'created', 'modified']
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
            tmstr = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(tmstmp))
            return tmstr
        elif columnName == 'modified':
            return len(self._configs[index.row()][columnName])
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
        request = self._connection.request_configs(
            {'config_type': config_type, 'discarded': self._discarded})
        if request['code'] == 200:
            self._configs = request['result']
        else:
            self._configs = []
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
        if not self._discarded:
            request = self._connection.delete_config(self._configs[row])
            if request['code'] != 200:
                self.connectionError.emit(
                    request['code'], request['message'],
                    'delete configuration')
                return False
        else:
            config = self._configs[row]
            full_config = self._getFullConfig(
                config['config_type'], config['name'])
            request = self._connection.retrieve_config(full_config)
            if request['code'] != 200:
                self.connectionError.emit(
                    request['code'], request['message'],
                    'retrieve configuration')
        self._configs = self._configs[:row] + self._configs[row + count:]
        self.endRemoveRows()
        return True

    def _getFullConfig(self, config_type, name):
        request = self._connection.get_config(config_type, name)
        if request['code'] != 200:
            self.connectionError.emit(
                request['code'], request['message'],
                'get configuration')
            return {}
        return request['result']
