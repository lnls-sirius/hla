"""Configuration window model definition."""
import re
from pydm.PyQt.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from pydm.PyQt.QtGui import QItemDelegate, QColor, QDoubleSpinBox
from siriuspy.servconf import ConfigurationPvs
from siriuspy.servconf.ConfigurationService import ConfigurationService


CONFIG_SERVICE_HOSTNAME = "guilherme-linux"


class Configuration:
    """Represents a configuration."""

    def __init__(self, name, config_type, values, id=None, new=True):
        """Init."""
        self._id = id
        self._name = name
        self._config_type = config_type
        self._values = values

        self._old_name = None
        self._renamed = False
        self._dirty_pvs = dict()
        self._is_new = new

    @classmethod
    def newConfiguration(configuration, name, config_type, values):
        """Create new configuration."""
        c = configuration(name, config_type, values)
        return c

    @classmethod
    def loadConfiguration(configuration, id):
        """Load existing configuration."""
        try:
            config = Configuration._load(id)  # Might fail
        except Exception as e:
            return False
        else:
            name = config["name"]
            config_type = config["config_type"]
            values = {}
            for value in config["values"]:
                values[value["pv_name"]] = value["value"]

            return configuration(name, config_type, values, id, False)

    @staticmethod
    def _load(id):
        db = ConfigurationService(CONFIG_SERVICE_HOSTNAME)
        resp = db.get_pv_configuration_by_id(id)

        if resp != 200:
            raise Exception("error")

        return db.get_result()[0]

    @staticmethod
    def delete(id):
        """Delete configuration."""
        db = ConfigurationService(CONFIG_SERVICE_HOSTNAME)
        resp = db.delete_pv_configuration(id)
        if resp != 200:
            raise Exception("server error {}".format(resp))

    @property
    def id(self):
        """Configuration id."""
        return self._id

    @property
    def name(self):
        """Configuration name."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Set new name to configuration."""
        if not self._renamed and not self._is_new:
            self._old_name = self._name
            self._renamed = True
        self._name = new_name

    @property
    def old_name(self):
        """Configuration name in database."""
        return self._old_name

    @property
    def values(self):
        """PV values."""
        return self._values

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
        db = ConfigurationService(CONFIG_SERVICE_HOSTNAME)
        if self._is_new:
            # Insert configuration
            resp = db.insert_pv_configuration(self._name, self._config_type)
            if resp != 200:
                raise Exception("sever error {}".format(resp))
            self._id = db.get_result()
            # Insert value
            data = []
            for pv_name, value in self._values.items():
                data.append({"pv_name": pv_name,
                             "pv_type": str(type(value)),
                             "value": value})
            resp = db.insert_pv_configuration_items(self._id, data)
            if resp != 200:
                raise Exception("sever error {}".format(resp))
            # Clear flags
            self._is_new = False

        else:
            if self._renamed:
                resp = db.update_pv_configuration(self._id, self._name)
                if resp != 200:
                    raise Exception("sever error {}".format(resp))
                self._renamed = False
            if len(self._dirty_pvs) > 0:
                for pv_name in self._dirty_pvs:
                    resp = db.update_pv_configuration_item(
                        self._id, pv_name, self._values[pv_name])
                    if resp != 200:
                        raise Exception("sever error {}".format(resp))
                self._dirty_pvs = dict()


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
                # element = ':'.join(pvname.split(":")[:2])
                # vheader = "{:02d} - {}".format(section + 1, element)
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
            # pvtype = self._vertical_header[row]['type']
            # cast_val = Configuration.castTo(value, pvtype)
            # Record action for UNDO
            config_name = self._configurations[col].name
            old_value = self._configurations[col].values[pvname]
            # cast_old_val = Configuration.castTo(old_value, pvtype)
            # Clean undo if it is the case
            if len(self._undo) > self.UNDO_MEMORY:
                self._undo.pop(0)
            # Append new undo action
            self._undo.append(
                (config_name,
                 lambda: self.setDataAlt(
                    row, config_name, value, old_value)))
            # self._undo.append(
            #     (config_name,
            #      lambda: self.setDataAlt(
            #         row, config_name, cast_val, cast_old_val)))
            # Update Value
            self._configurations[col].setValue(pvname, value)
            # self._configurations[col].setValue(pvname, cast_val)
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
        pvs = getattr(ConfigurationPvs, self._config_type)().pvs()
        for name, type_ in pvs.items():
            self._vertical_header.append({'name': name, 'type': type_})
        self._vertical_header.sort(
            key=lambda x: elem(x['name']) + subSection(x['name']))

    def _addConfiguration(self, column, id=None,
                          config_name=None, values=None):
        """Add new configuration to table."""
        # Create new configuration
        if id is not None:
            new_configuration = Configuration.loadConfiguration(id)
            if not new_configuration:
                raise \
                    FileNotFoundError("Configuration {} not found".format(id))
            # if not new_configuration.check():
            #     raise KeyError(
            #         "Configuration {} corrupted".format(config_name))
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

    def getConfigurations(self):
        """Return name of saved configurations."""
        # connection = db.get_connection()
        # with connection.cursor() as cursor:
        #     sql = "SELECT name FROM configuration WHERE classname=%s"
        #     # r = cursor.execute(sql, (self._config_type))
        #     cursor.execute(sql, (self._config_type))
        #     qry_res = cursor.fetchall()
        #
        # configurations = [x['name'] for x in qry_res]
        db = ConfigurationService(CONFIG_SERVICE_HOSTNAME)
        resp = db.get_pv_configurations({"config_type": self._config_type})
        if resp != 200:
            raise Exception("server error {}".format(resp))
        return db.get_result()

    def getTuneMatrix(self):
        """Get tune matrix from db."""
        db = ConfigurationService(CONFIG_SERVICE_HOSTNAME)
        resp = db.get_configuration("tune_matrix")
        if resp != 200:
            raise Exception("server error {}".format(resp))
        return db.get_result()["value"]
    #     conn = db.get_connection()
    #     with conn.cursor() as cursor:
    #         sql = ("SELECT `line`, `column`, value "
    #                "FROM parameter_values "
    #                "WHERE name='standard_matrix' AND type='tune' "
    #                "ORDER BY `line`, `column`")
    #         # ret = cursor.execute(sql)
    #         cursor.execute(sql)
    #         qry = cursor.fetchall()
    #
    #     new_line = list()
    #     last_line = -1
    #     result = list()
    #     for row in qry:
    #         line = row['line']
    #         if line != last_line:
    #             if last_line > -1:
    #                 result.append(new_line)
    #             last_line = line
    #             new_line = list()
    #
    #         if row['column'] == len(new_line):
    #             new_line.append(row['value'])
    #         else:
    #             return 0
    #     result.append(new_line)
    #
    #     if len(result) > 1:
    #         return result
    #     else:
    #         return result[0]

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

    def loadConfiguration(self, id=None, name=None, values=None):
        """Load configuration from database."""
        if id is not None:  # Load existing config
            self._addConfiguration(self.columnCount(), id=id)
        else:  # New config
            self._addConfiguration(
                self.columnCount(), config_name=name, values=values)

    def deleteConfiguration(self, id, config):
        """Delete configuration from database."""
        col = self.getConfigurationColumn(config)
        if col >= 0:
            self.closeConfiguration(col)
        return Configuration.delete(id)

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
