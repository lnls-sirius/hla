"""Model to get all config types registered."""

from qtpy.QtCore import Qt, QAbstractListModel


class ConfigTypeModel(QAbstractListModel):
    """."""

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
        dbase = self._connection.get_config_types()
        templ = self._connection.get_config_types_from_templates()
        config_types = sorted(set(dbase + templ))
        self._configs.extend(config_types)
        self.endResetModel()


class ConfigPVsTypeModel(ConfigTypeModel):
    """."""

    def setupModelData(self):
        """Set model data up."""
        self.beginResetModel()
        self._configs = ['Select a configuration type...', ]

        # sort all configs of PV type
        conn = self._connection
        allconfs = conn.get_config_types_from_template()
        configs = [c for c in allconfs if 'pvs' in
                   conn.get_value_from_template(c)]
        configs = sorted(configs)

        # move 'global_config' to begin, if it exists
        try:
            configs.remove('global_config')
            configs.insert(0, 'global_config')
        except ValueError:
            pass

        self._configs.extend(configs)
        self.endResetModel()
