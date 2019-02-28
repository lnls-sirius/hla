"""Model to get all config types registered."""

from qtpy.QtCore import Qt, QAbstractListModel

from siriuspy.servconf.conf_types import get_config_type_template


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
        self._configs.extend(self._connection.get_config_types())
        self.endResetModel()


class ConfigPVsTypeModel(ConfigTypeModel):

    def setupModelData(self):
        """Setup model data."""
        self.beginResetModel()
        self._configs = ['Select a configuration type...', ]
        configs = [c for c in self._connection.get_config_types()
                   if 'pvs' in get_config_type_template(c)]
        self._configs.extend(sorted(configs))
        self.endResetModel()
