import re, pymysql
from siriuspy.pwrsupply import psdata
from datetime import datetime, timezone, timedelta
from pydm.PyQt.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, \
        QAbstractItemModel
from pydm.PyQt.QtGui import QItemDelegate, QApplication, QTextDocument, \
        QStyle, QColor, QPalette
from as_ps_cycle.PowerSupply import PowerSupply

class Configuration:
    _name = ''
    _values = list()

    _dirty_pvs = list()

    _dirty = False
    _renamed = False
    _isNew = False

    _old_name = None

    def __init__(self, connection, name, values, isNew=False):
        self._name = name
        self._values = values
        self._isNew = isNew
        self._connection = connection

    def getValue(self, idx):
        return self._values[idx]['value']

    def setValue(self, idx, value):
        self._values[idx]['value'] = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def old_name(self):
        return self._old_name

    @old_name.setter
    def old_name(self, value):
        self._old_name = value

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = values

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        self._dirty = value

    @property
    def renamed(self):
        return self._renamed

    @renamed.setter
    def renamed(self, value):
        self._renamed = value

    @property
    def isNew(self):
        return self._isNew

    @isNew.setter
    def isNew(self, value):
        self._isNew = value

    def isSaved(self):
        if self._dirty or self._renamed or self._isNew:
            return False

        return True

    #Actions
    def rename(self, new_name):
        if not self._renamed:
            self._old_name = self._name
        self._name = new_name
        self._renamed = True

    def save(self):
        if self._renamed:
            self.updateName()
        if self._dirty or self._isNew:
            with self._connection.cursor() as cursor:
                if self._isNew:
                    sql = ( "INSERT INTO element_config(name, area) "
                            "VALUES (%s, 'BO')")
                    cursor.execute(sql, (self._name))

                    for pvname, value in self._values.items():
                        sql = ( "INSERT INTO config_values"
                                "(config_name, pvname, value) "
                                "VALUES (%s, %s, %s)")
                        cursor.execute(sql, (self._name, pvname, value))
                else:
                    for pvname, value in self._values.items():
                        sql =   ("UPDATE config_values SET value=%s "
                                "WHERE config_name=%s AND pvname=%s")
                        cursor.execute(sql, (value, self._name, pvname))

                self._connection.commit()
                self._dirty = self._isNew = False

    def updateName(self):
        try:
            with self._connection.cursor() as cursor:
                #Update database
                sql = "UPDATE element_config SET name=%s WHERE name=%s"
                cursor.execute(sql, (self._name, self._old_name))
                self._connection.commit()
                #print("Updated from {} to {}".format(self._old_name, self._name))
                self._renamed = False
        finally:
            pass

class ConfigDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(ConfigDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not index.model().isColumnSaved(index.column()):
            color = QColor(230, 230, 230)
            painter.fillRect(option.rect, color)
            QItemDelegate.paint(self, painter, option, index)
        else:
            QItemDelegate.paint(self, painter, option, index)

class ConfigModel(QAbstractTableModel):

    TUNE, CHROMATICITY = range(2)

    def __init__(self, parent=None):
        super(ConfigModel, self).__init__(parent)

        self._vertical_header = list()
        self._configurations = list()
        self._elems = None
        self._buildBoosterDict()
        self._connection = pymysql.connect( host='localhost',
                                            user='root',
                                            password='root',
                                            db='sirius',
                                            charset='utf8mb4',
                                            cursorclass=pymysql.cursors.DictCursor)

    def __del__(self):
        self._connection.close()

    @property
    def configurations(self):
        return self._configurations

    #QAbstractTableModel Overriden functions
    def rowCount(self, index=QModelIndex()):
        return len(self._vertical_header)

    def columnCount(self, index=QModelIndex()):
        return len(self._configurations)

    def data(self, index, role=Qt.DisplayRole):
        ''' (override) Sets data of the table '''
        if role == Qt.DisplayRole:
            pvname = self._vertical_header[index.row()]
            return QVariant(self._configurations[index.column()].values[pvname])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        ''' (override) Sets headers of the table '''
        if role == Qt.TextAlignmentRole:
            pass
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if self._configurations[section].isSaved():
                return QVariant(self._configurations[section].name)
            else:
                return QVariant(self._configurations[section].name + "*")
        elif orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                element = ':'.join(self._vertical_header[section].split(":")[:2])
                #vheader = "{:02d} - {}".format(section + 1, element)
                vheader = "{}".format(element)
                return QVariant(vheader)

        return QVariant(int(section + 1))

    def insertColumn(self, column, index=QModelIndex()):
        ''' Updates table widget telling it a new column was inserted (override)'''
        self.beginInsertColumns(index, column, column)
        self.endInsertColumns()

        return True

    def removeColumns(self, column, count=1, index=QModelIndex()):
        self.beginRemoveColumns(index, column, column + count - 1)
        self.endRemoveColumns()

        return True

    #Used to sort
    def _section(self, elem):
        if re.search('-Fam', elem.devName()):
            return 0
        else:
            return 1
    def _elem(self, elem):
        name = elem.devName()
        if re.search('-B', name):
            return 0
        elif re.search('-Q(F|D|[0-9])', name):
            return 2
        elif re.search('-S(F|D)', name):
            return 4
        elif re.search('-CH', name):
            return 6
        elif re.search('-CV', name):
            return 8
        elif re.search('-FCH', name):
            return 10
        elif re.search('-FCV', name):
            return 12
        else:
            return 14

    #Private members
    def _buildBoosterDict(self):
        if self._elems is None:
            ps = psdata.get_names()
            self._elems = [PowerSupply(x) for x in ps if re.match("^BO", x)]
            self._elems.sort(key=lambda x: self._elem(x) + self._section(x))

        for i, ps in enumerate(self._elems):
            pv = ps.devName() + ":" + ps.force + "-RB"
            #self._pvnames.append(pv)
            self._vertical_header.append(pv)

    def _elementCheck(self, values):
        ''' Checks if all pvnames exist '''
        for pvname in self._vertical_header:
            if pvname not in values.keys():
                return False

        return True

    def _addConfiguration(self, config_name, column, values, is_new=True):
        ''' Adds new configuration to table '''
        #Insert new configuration
        if column >= self.columnCount():
            self._configurations.append(Configuration(self._connection, config_name, values, is_new))
        else:
            self._configurations.insert(column, Configuration(self._connection, config_name, values, is_new))
        #Call insertColumns to update table widget
        self.insertColumn(column)

    ##
    def loadConfiguration(self, config):
        ''' Loads configuration from database '''
        with self._connection.cursor() as cursor:
            sql = "SELECT pvname, value FROM config_values WHERE config_name=%s"
            result = cursor.execute(sql, (config))
            if not result:
                raise ValueError("Configuration {} not found".format(config))
            qry_res = cursor.fetchall()

            config_values = dict()
            for pv in qry_res:
                config_values[pv['pvname']] = pv['value']

            if self._elementCheck(config_values):
                #values = [v['value'] for v in qry_res]
                self._addConfiguration(config, self.columnCount(), config_values, is_new=False)
            else: #TODO in this case the set of elements changed
                pass
            #print("Configuration {} loaded".format(config))

    def loadCurrentConfiguration(self, name):
        ''' Loads current state of booster element '''
        config = dict()
        for i, ps in enumerate(self._elems):
            force = ps.readCurrent() # readForce
            if force is None:
                force = -1
            pvname = '{}:{}-RB'.format(ps.devName(), ps.force)
            config[pvname] = force
        #Add new configuration
        self._addConfiguration(name, self.columnCount(), config)

    def getConfigurations(self):
        ''' Returns name of saved configurations '''
        with self._connection.cursor() as cursor:
            sql = "SELECT name FROM element_config WHERE area='BO'";
            r = cursor.execute(sql)
            qry_res = cursor.fetchall()

        return [x['name'] for x in qry_res]

    #Interface functions view - model
    def columnState(self, column):
        return (self._configurations[column].dirty,     \
                self._configurations[column].renamed,   \
                self._configurations[column].isNew)

    def isColumnSaved(self, column):
        return self._configurations[column].isSaved()

    def getConfigurationName(self, column):
        return self._configurations[column].name;

    def getConfigurationColumn(self, config_name):
        for configuration in self._configurations:
            if config_name in (configuration.name, configuration.old_name):
                return self._configurations.index(configuration)

        return -1


    #Actions
    def saveConfiguration(self, column):
        if not self._configurations[column].isSaved():
            self._configurations[column].save()
        idx1 = self.index(0, column)
        idx2 = self.index(self.rowCount() - 1, column)
        self.dataChanged.emit(idx1, idx2)
        self.headerDataChanged.emit(Qt.Horizontal, column, column)

    def renameConfiguration(self, column, new_name):
        self._configurations[column].rename(new_name)

    def deriveConfiguration(self, config_name, base_column, func, parameters):
        ''' Applies a function to a configuration, generating a new one'''
        #Sets configuration name and value
        new_configuration = dict()
        for pvname in self._vertical_header:
            value = self._configurations[base_column].values[pvname]
            if func == self.TUNE:
                if re.search("-QD", pvname):
                    new_value = value + parameters[0]
                elif re.search("QF", pvname):
                    new_value = value + parameters[1]
                else:
                    new_value = value
            else:
                new_value = value
            new_configuration[pvname] = new_value
        #Add configuration to table as a new column
        self._addConfiguration(config_name, base_column+1, new_configuration)

    def closeConfiguration(self, column):
        self._configurations.remove(self._configurations[column])
        self.removeColumns(column)

    def interpolateConfiguration(self, config_name, column1, column2):
        ''' Linear interpolation of 2 configurations '''
        new_configuration = dict()
        for pvname in self._vertical_header:
            value1 = self._configurations[column1].values[pvname]
            value2 = self._configurations[column2].values[pvname]
            new_configuration[pvname] = (value1 + value2)/2
        #Add configuration to table as a new column
        new_column = column1 if column1 > column2 else column2
        self._addConfiguration(config_name, new_column + 1, new_configuration)
