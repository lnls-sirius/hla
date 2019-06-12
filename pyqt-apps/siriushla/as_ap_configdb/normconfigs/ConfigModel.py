"""Configuration window model definition."""
import re
from qtpy.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from qtpy.QtWidgets import QItemDelegate, QDoubleSpinBox
from qtpy.QtGui import QColor
from siriuspy.clientconfigdb import ConfigDBClient


class Configuration:
    """Represents a configuration."""

    def __init__(self, name, config_type, values, new=True):
        """Init."""
        self._name = name
        self._config_type = config_type
        self._values = values['pvs']

        self._old_name = None
        self._renamed = False
        self._dirty_pvs = dict()
        self._is_new = new

    @staticmethod
    def newConfiguration(name, config_type, values):
        """Create new configuration."""
        return Configuration(name, config_type, values)

    @staticmethod
    def loadConfiguration(config_type, name):
        """Load existing configuration."""
        config = Configuration._load(config_type, name)  # Might fail
        name = config["name"]
        config_type = config["config_type"]
        values = config["value"]
        return Configuration(name, config_type, values, False)

    @staticmethod
    def _load(config_type, name):
        db = ConfigDBClient()
        data = db.get_config_info(name, config_type=config_type)
        data['value'] = db.get_config_value(name, config_type=config_type)
        return data

    @staticmethod
    def delete_config(config_type, name):
        """Delete configuration."""
        db = ConfigDBClient()
        return db.delete_config(name, config_type=config_type)

    @property
    def name(self):
        """Configuration name."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Set new name to configuration."""
        if new_name == self._old_name:
            self._renamed = False
            self._name = self._old_name
        else:
            self._renamed = True
            self._old_name = self._name
            self._name = new_name

    @property
    def old_name(self):
        """Configuration name in database."""
        return self._old_name

    @property
    def values(self):
        """PV values."""
        return {'pvs': self._values}

    @property
    def dirty(self):
        """Return wether thre is unsaved data."""
        if len(self._dirty_pvs) > 0 or self._renamed or self._is_new:
            return True
        return False

    def setValue(self, pv_name, value):
        """Set value of a given pv."""
        if value != self._values[pv_name]:
            # If the configuration is new there is no need to set dirty flags
            if not self._is_new:
                # Clean dirty flag
                if pv_name in self._dirty_pvs.keys() \
                        and value == self._dirty_pvs[pv_name]:
                    del self._dirty_pvs[pv_name]
                # Set dirty flag
                elif pv_name not in self._dirty_pvs.keys():
                    self._dirty_pvs[pv_name] = self._values[pv_name]
            # Finally set value
            self._values[pv_name] = value

    def save(self):
        """Save data."""
        db = ConfigDBClient()
        if self._is_new or self._renamed or self._dirty_pvs:
            # Insert configuration
            db.insert_config(
                self._name, {'pvs': self._values},
                config_type=self._config_type)
            # Clear flags
            self._is_new = False
            self._renamed = False
            self._dirty_pvs = dict()

    def delete(self):
        """Delete configuration."""
        db = ConfigDBClient()
        db.delete_config(self._name, config_type=self._config_type)


class ConfigDelegate(QItemDelegate):
    """Styling."""

    def paint(self, painter, option, index):
        """Override paint function.

        Responsible for painting dirt columns and cells.
        """
        col = index.column()
        pvname = index.model()._vertical_header[index.row()]['name']
        if pvname in index.model().configurations[col]._dirty_pvs.keys():
            color = QColor(200, 0, 0)
            painter.fillRect(option.rect, color)
            QItemDelegate.paint(self, painter, option, index)
        elif index.model().configurations[col].dirty:
            color = QColor(230, 230, 230)
            painter.fillRect(option.rect, color)
            QItemDelegate.paint(self, painter, option, index)
        else:
            QItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        """Override.

        Create and editor based on the cell type
        """
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(5)
        return editor

    def setEditorData(self, editor, index):
        """Override.

        Set cell data as float.
        """
        value = index.model().data(index, Qt.DisplayRole)
        editor.setValue(float(value.value()))


class ConfigModel(QAbstractTableModel):
    """Model for the configuration table."""

    TUNE, CHROMATICITY = range(2)
    UNDO_MEMORY = 75

    def __init__(self, config_type, parent=None):
        """Class constructor."""
        super(ConfigModel, self).__init__(parent)

        self._config_type = config_type
        self._setVerticalHeader()
        self._types = set()
        self._configurations = list()
        self._undo = list()
        self._redo = list()

    @property
    def configurations(self):
        """Return list of open configurations."""
        return self._configurations

    # QAbstractTableModel Overriden functions
    def rowCount(self, index=QModelIndex()):
        """Return the number of PVs for this configuration type."""
        return len(self._vertical_header)

    def columnCount(self, index=QModelIndex()):
        """Return the number of configurations currently open."""
        return len(self._configurations)

    def data(self, index, role=Qt.DisplayRole):
        """Set data of the table (override)."""
        if role == Qt.DisplayRole:
            pvname = self._vertical_header[index.row()]['name']
            pvtype = self._vertical_header[index.row()]['type']
            if pvtype == float:
                return QVariant("{:8.5f}".format(
                    self._configurations[index.column()].values[pvname]))
            else:
                raise NotImplementedError

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Set headers of the table (override)."""
        if role == Qt.TextAlignmentRole:
            pass
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if not self._configurations[section].dirty:
                return QVariant(self._configurations[section].name)
            else:
                return QVariant(self._configurations[section].name + "*")
        elif orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                pvname = self._vertical_header[section]['name']
                vheader = "{}".format(pvname)
                return QVariant(vheader)

        return QVariant(int(section + 1))

    def flags(self, index):
        """Override to make cells editable."""
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole):
        """Set cell data."""
        row = index.row()
        col = index.column()
        if index.isValid() and 0 <= row < len(self._vertical_header):
            pvname = self._vertical_header[row]['name']
            config_name = self._configurations[col].name
            old_value = self._configurations[col].values[pvname]
            # Clean undo if it is the case
            if len(self._undo) > self.UNDO_MEMORY:
                self._undo.pop(0)
            # Append new undo action
            self._undo.append(
                (config_name, lambda: self.setDataAlt(row, config_name,
                                                      value, old_value)))
            # Update Value
            self._configurations[col].setValue(pvname, value)
            # Update view
            self.headerDataChanged.emit(Qt.Horizontal, col, col)
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertColumn(self, column, index=QModelIndex()):
        """Update table widget telling it a new column was inserted."""
        self.beginInsertColumns(index, column, column)
        self.endInsertColumns()

        return True

    def removeColumns(self, column, count=1, index=QModelIndex()):
        """Update table widget telling it a column was removed."""
        self.beginRemoveColumns(index, column, column + count - 1)
        self.endRemoveColumns()

        return True

    # Private members
    def _setVerticalHeader(self):
        # Used to sort section elements dict
        def subSection(elem):
            if re.search('-Fam', elem):
                return 0
            else:
                return 1

        def elem(elem):
            name = elem
            if re.search('-B', name):
                return 0
            elif re.search('-QF', name):
                return 2
            elif re.search('-QD', name):
                return 4
            elif re.search('-Q[0-9]', name):
                return 6
            elif re.search('-SF', name):
                return 8
            elif re.search('-SD', name):
                return 10
            elif re.search('-CH', name):
                return 12
            elif re.search('-CV', name):
                return 14
            elif re.search('-FCH', name):
                return 16
            elif re.search('-FCV', name):
                return 18
            else:
                return 20

        self._vertical_header = list()
        client = ConfigDBClient()
        if self._config_type == 'bo_normalized':
            pvs = client.get_value_template('bo_normalized')['pvs']
        elif self._config_type == 'si_normalized':
            pvs = client.get_value_template('si_normalized')['pvs']
        else:
            raise Exception("Module {} not found".format(self._config_type))
        # pvs = get_dict()["value"]
        # pvs = getattr(ConfigurationPvs, self._config_type)().pvs()
        for name, value, _ in pvs:
            self._vertical_header.append({'name': name, 'type': type(value)})
        self._vertical_header.sort(
            key=lambda x: elem(x['name']) + subSection(x['name']))

    def _addConfiguration(self, column, id=None,
                          config_name=None, values=None):
        """Add new configuration to table."""
        # Create new configuration
        if values is None:
            new_configuration = Configuration.loadConfiguration(
                self._config_type, config_name)
        else:
            new_configuration = Configuration.newConfiguration(
                config_name, self._config_type, values)
        # Add to model in case it was successfully created
        if column >= self.columnCount():
            self._configurations.append(new_configuration)
        else:
            self._configurations.insert(column, new_configuration)
        # Call insertColumns to update table widget
        self.insertColumn(column)

    # Interface functions view - model
    def getConfigurationColumn(self, config_name):
        """Return column number of the given configuration."""
        for configuration in self._configurations:
            if config_name in (configuration.name, configuration.old_name):
                return self._configurations.index(configuration)

        return -1

    def getConfigurations(self, deleted=False):
        """Return name of saved configurations."""
        db = ConfigDBClient()
        return db.find_configs(
            config_type=self._config_type, discarded=deleted)

    def getTuneMatrix(self):
        """Get tune matrix from db."""
        db = ConfigDBClient()
        return db.get_config_value("tune_matrix", "tune_matrix")

    # Actions
    def saveConfiguration(self, column):
        """Save configuration if it is dirty."""
        if self._configurations[column].dirty:
            self._configurations[column].save()
        # Issue a change in the table and header
        idx1 = self.index(0, column)
        idx2 = self.index(self.rowCount() - 1, column)
        self.dataChanged.emit(idx1, idx2)
        self.headerDataChanged.emit(Qt.Horizontal, column, column)

    def renameConfiguration(self, column, new_name):
        """Change configuration name."""
        self._configurations[column].name = new_name

    def deriveConfiguration(self, config_name, base_column, func, parameters):
        """Create new configuration from existing one TUNE or CHROMATICITY."""
        # Derives new configuration
        new_configuration = dict()
        for pv in self._vertical_header:
            pvname = pv['name']
            # pvtype = pv['type']
            value = self._configurations[base_column].values[pvname]
            if func == self.TUNE:  # Applied to quadrupoles
                if re.search("-QD", pvname):
                    new_value = value + parameters[0]
                elif re.search("QF", pvname):
                    new_value = value + parameters[1]
                else:
                    new_value = value
            elif func == self.CHROMATICITY:
                new_value = value
            else:
                new_value = value
            new_configuration[pvname] = new_value
        # Add configuration to table as a new column
        self._addConfiguration(
            base_column+1, config_name=config_name, values=new_configuration)

    def closeConfiguration(self, column):
        """Close a configuration."""
        self._configurations.remove(self._configurations[column])
        self.removeColumns(column)

    def interpolateConfiguration(self, config_name, column1, column2):
        """Linear interpolation of 2 configurations."""
        for type_ in self._getTypes():
            if type_ not in [int, float]:
                raise ValueError("Cannot interpolate non-numeric values")

        new_configuration = dict()
        for pv in self._vertical_header:
            pvname = pv['name']
            value1 = self._configurations[column1].values[pvname]
            value2 = self._configurations[column2].values[pvname]
            new_configuration[pvname] = (value1 + value2)/2
        # Choose where to place new column
        new_column = column1 if column1 > column2 else column2
        self._addConfiguration(
            new_column + 1, config_name=config_name, values=new_configuration)

    def loadConfiguration(self, name=None, values=None):
        """Load configuration from database."""
        if values is None:  # Load existing config
            self._addConfiguration(self.columnCount(), config_name=name)
        else:  # New config
            self._addConfiguration(
                self.columnCount(), config_name=name, values=values)

    def deleteConfiguration(self, config_info):
        """Delete configuration from database."""
        col = self.getConfigurationColumn(config_info["name"])
        Configuration.delete_config(config_info['config_type'], config_info['name'])
        if col >= 0:
            self.closeConfiguration(col)

    # Implements undo/redo
    def setDataAlt(self, row, config_name, value, old_value, redo=True):
        """Called by the undo/redo methods to change data on table."""
        pvname = self._vertical_header[row]['name']
        # pvtype = self._vertical_header[row]['type']
        column = self.getConfigurationColumn(config_name)
        index = self.index(row, column)
        self._configurations[column].setValue(pvname, old_value)
        if redo:
            # Clean redo if bigger than memort
            if len(self._redo) > self.UNDO_MEMORY:
                self._redo.pop(0)
            # Append new redo action
            self._redo.append(
                (config_name,
                 lambda: self.setDataAlt(
                    row, config_name, old_value, value, False)))
        else:
            # Clean undo if bigger than memory
            if len(self._undo) > self.UNDO_MEMORY:
                self._undo.pop(0)
            # Append new undo action
            self._undo.append(
                (config_name,
                 lambda: self.setDataAlt(
                    row, config_name, old_value, value, True)))
        # Update view
        self.headerDataChanged.emit(
            Qt.Horizontal, index.column(), index.column())
        self.dataChanged.emit(index, index)

    def cleanUndo(self, column):
        """Clean undo/redo actions for given column."""
        config_name = self._configurations[column].name
        for i, action in enumerate(self._undo):
            if action[0] == config_name:
                self._undo.pop(i)

        for i, action in enumerate(self._redo):
            if action[0] == config_name:
                self._redo.pop(i)

    def _getTypes(self):
        if not self._types:
            for pv in self._vertical_header:
                self._types.add(pv['type'])
        return self._types
