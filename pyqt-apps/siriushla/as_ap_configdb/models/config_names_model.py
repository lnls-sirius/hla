"""Model to get registered configuration names for a given type."""
from qtpy.QtCore import Qt, QAbstractListModel

from siriuspy.clientconfigdb import ConfigDBException


class ConfigNamesModel(QAbstractListModel):
    """Model that gets a list of names given a configuration type."""

    def __init__(self, connection, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._config_type = None
        self._connection = connection
        self.setupModelData()

    @property
    def config_type(self):
        """Configuration type."""
        return self._config_type

    @config_type.setter
    def config_type(self, value):
        self._config_type = value
        self.setupModelData()

    def rowCount(self, index):
        """Return number of configurations."""
        return len(self._items)

    def columnCount(self, index):
        """Return number of columns."""
        return 1

    def data(self, index, role=Qt.DisplayRole):
        """Return data at index."""
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        return self._items[index.row()]

    def setupModelData(self):
        """Setup model data."""
        self.beginResetModel()
        if self._config_type is None:
            self._items = ['No configuration found...', ]
        else:
            try:
                ret = self._connection.find_configs(
                    config_type=self._config_type)
                if ret:
                    self._items = ['Select a configuration...', ]
                    self._items.extend(sorted([r['name'] for r in ret]))
                else:
                    self._items = ['No configuration found...', ]
            except ConfigDBException as err:
                self._items = [err.server_message, ]
        self.endResetModel()
