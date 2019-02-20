"""Model to get all config types registered."""

from qtpy.QtCore import Qt, QAbstractListModel


class ConfigTypeModel(QAbstractListModel):

    def __init__(self, connection, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._connection = connection
        self.setupModelData()

    def rowCount(self, index):
        """Return number of configurations."""
        return len(self._configs)

    def columnCount(self, index):
        """Return number of columns."""
        return 1

    def data(self, index, role=Qt.DisplayRole):
        """Return data at index."""
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        return self._configs[index.row()]

    def setupModelData(self):
        """Setup model data."""
        self.beginResetModel()
        self._configs = ['Select a configuration type...', ]
        self._configs.extend(sorted(self._connection.get_config_types()))
        # ret = self._connection.get_types()
        # if ret['code'] == 200:
        #     self._configs = ['Select a configuration type...', ]
        #     self._configs.extend(sorted(ret['result']))
        # else:
        #     self._configs = [ret['message'], ]
        self.endResetModel()
