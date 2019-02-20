"""Model that gets the pvs field of configuration type."""
from qtpy.QtCore import Qt, QAbstractTableModel
from siriuspy.servconf.conf_types import get_config_type_template


class PVConfigurationTableModel(QAbstractTableModel):
    """Table model with PVs from a given type of configuration."""

    def __init__(self, config_type=None, parent=None):
        """Constructor.

        config_type: configuration type name
        connection: connection object
        """
        super().__init__(parent)
        self._config_type = config_type
        self._data = list()
        self.setupModelData()

    @property
    def model_data(self):
        """Data."""
        return self._data

    @property
    def config_type(self):
        """Configuration type."""
        return self._config_type

    @config_type.setter
    def config_type(self, value):
        self._config_type = value
        self.setupModelData()

    def rowCount(self, index):
        """Return number of rows."""
        return len(self._data)

    def columnCount(self, index):
        """Return number of columns."""
        try:
            return len(self._data[0])
        except IndexError:
            return 0

    def data(self, index, role=Qt.DisplayRole):
        """Return data at index."""
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        column = index.column()
        row = index.row()

        return self._data[row][column]

    def headerData(self, section, orientation, role):
        """Return header."""
        if orientation == Qt.Horizontal:
            if section == 0:
                return 'PV'
            elif section == 1:
                return 'Value'
            elif section == 2:
                return 'Delay'
        return super().headerData(section, orientation, role)

    def setupModelData(self):
        """Setup model data."""
        if self._config_type is None:
            return
        self.beginResetModel()
        config = get_config_type_template(self._config_type)
        if 'pvs' in config:
            self._data = config['pvs']
            # self._data.sort(key=lambda x: x[0])
        self.endResetModel()

    def flags(self, index):
        """Override to make cells editable."""
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() in (2, ):
            return Qt.ItemFlags(
                QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)
        return QAbstractTableModel.flags(self, index)

    def setData(self, index, value, role=Qt.EditRole):
        """Set data."""
        if not index.isValid():
            return False

        column = index.column()
        row = index.row()

        if column == 0:
            return False

        if column == 1:
            self._data[row][column] = value
            self.dataChanged.emit(index, index)

        if column == 2:
            self._data[row][column] = float(value)
            self.dataChanged.emit(index, index)

        return True
