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
        """Set model data up."""
        self.beginResetModel()
        self._configs = ['Select a configuration type...', ]
        self._configs.extend(self._connection.get_config_types())
        self.endResetModel()


class ConfigPVsTypeModel(ConfigTypeModel):

    def setupModelData(self):
        """Set model data up."""
        self.beginResetModel()
        self._configs = ['Select a configuration type...', ]

        # sort all configs of PV type
        allconfigs = self._connection.get_config_types()
        configs = [c for c in allconfigs
                   if 'pvs' in get_config_type_template(c)]
        configs = sorted(configs)

        # move 'global_config' to begin, if it exists
        try:
            configs.remove('global_config')
            configs.insert(0, 'global_config')
        except ValueError:
            pass

        self._configs.extend(configs)
        self.endResetModel()
