"""Window to manage configurations."""
import logging
import time

from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, \
    QWidget, QFrame, QLabel, QComboBox, QPushButton, QMessageBox, QTabWidget, \
    QTableView, QTreeView, QHeaderView
from qtpy.QtCore import Qt, pyqtSlot, pyqtSignal, QModelIndex, \
    QAbstractItemModel, QAbstractTableModel

from siriushla.widgets.windows import SiriusMainWindow


class TreeItem:
    """An item of a tree."""

    def __init__(self, data, parentItem):
        """Set item data and its parent item."""
        self._childItems = list()
        self._itemData = data
        self._parentItem = parentItem

    def appendChild(self, item):
        """Append a child item."""
        self._childItems.append(item)

    def child(self, row):
        """Return child at given row."""
        return self._childItems[row]

    def childCount(self):
        """Return number of children."""
        return len(self._childItems)

    def columnCount(self):
        """Return number of columns of data."""
        return len(self._itemData)

    def data(self, column):
        """Return data at given column."""
        return self._itemData[column]

    def row(self):
        """Report the item's location within its parent's list of items."""
        if self._parentItem is not None:
            return self._parentItem._childItems.index(self)
        return 0

    def parentItem(self):
        """Return parent item."""
        return self._parentItem


class JsonTreeModel(QAbstractItemModel):
    """Model for a tree that represent a JSON document."""

    def __init__(self, config_type, name, connection, parent=None):
        """Set model data."""
        super().__init__(parent)
        self._rootItem = TreeItem(['Key', 'Value'], None)
        self._connection = connection
        self.setupModelData([(config_type, name)])

    def index(self, row, column, parent):
        """Provide and index."""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        """Return parent of given index."""
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parentItem()

        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        """Return index row count."""
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent):
        """Return index column count."""
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self._rootItem.columnCount()

    def data(self, index, role):
        """Return data at index."""
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def flags(self, index):
        """Read-only."""
        if not index.isValid():
            return 0

        return QAbstractItemModel.flags(self, index)

    def headerData(self, section, orientation, role):
        """Return data stored in root item."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._rootItem.data(section)

        return None

    def setupModelData(self, config_list):
        """Set model data."""
        # Parse json data to python structures
        configs = list()
        for config_type, name in config_list:
            request = self._connection.get_config(config_type, name)
            if request['code'] == 200:
                if 'modified' in request['result']:
                    request['result']['modified'] = \
                        [time.strftime(
                            '%d/%m/%Y %H:%M:%S', time.localtime(float(t)))
                         for t in request['result']['modified']]
                configs.append(request['result'])
            else:
                configs.append(request['code'])
        self._fillTree(configs)

    def _fillTree(self, config):
        """Fill tree."""
        self.beginResetModel()
        self._rootItem = TreeItem(['Key', 'Value'], None)
        # Fill tree
        if len(config) == 1:
            self._addChildren(self._rootItem, config[0])
        else:
            self._addChildren(self._rootItem, config)
        self.endResetModel()

    def _addChildren(self, item, config):
        """Add children."""
        if isinstance(config, dict):
            for key, val in config.items():
                if isinstance(val, (list, dict)):  # Has children
                    new_item = TreeItem([key, ''], item)
                    self._addChildren(new_item, val)
                    item.appendChild(new_item)
                else:
                    item.appendChild(TreeItem([key, str(val)], item))
        elif isinstance(config, list):
            for idx, value in enumerate(config):
                if isinstance(value, (list, dict)):  # Has children
                    new_item = TreeItem([str(idx), ''], item)
                    # new_item = QTreeWidgetItem([str(idx), ''])
                    self._addChildren(new_item, value)
                    item.appendChild(new_item)
                else:
                    item.appendChild(TreeItem([str(idx), str(value)], item))


class ConfigDbTableModel(QAbstractTableModel):
    """Model for configuration database."""

    removeRow = pyqtSignal(QModelIndex)
    connectionError = pyqtSignal(int, str, str)

    def __init__(self, config_type, connection, discarded=False, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._connection = connection
        self._discarded = discarded
        self.horizontalHeader = \
            ['config_type', 'name', 'created', 'modified']
        self.setupModelData(config_type)

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
        if index.column() == self.horizontalHeader.index('name'):
            return Qt.ItemFlags(
                QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)
        else:
            return QAbstractItemModel.flags(self, index)

    def setData(self, index, value, role=Qt.EditRole):
        """Set cell data."""
        if not index.isValid():
            return False

        if not value:
            return False

        if index.column() == self.horizontalHeader.index('name'):
            config = self._configs[index.row()]
            full_config = self._getFullConfig(
                config['config_type'], config['name'])
            full_config['name'] = value
            try:
                request = self._connection.update_config(full_config)
            except Exception as e:
                self.connectionError.emit(
                    'Exception', '{}'.format(e),
                    'update configuration')
                return False
            if request['code'] != 200:
                self.connectionError.emit(
                    request['code'], request['message'],
                    'update configuration')
                return False

            full_config = self._getFullConfig(
                config['config_type'], config['name'])
            config = full_config
            # config['name'] = value
            self.dataChanged.emit(index, index)
        return True

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
            full_config['name'] = full_config['name'][:-37]
            full_config['discarded'] = False
            request = self._connection.update_config(full_config)
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


class ConfigurationManager(SiriusMainWindow):
    """."""

    NAME_COL = None
    CONFIG_TYPE_COL = None
    Stylesheet = """
        * {
            font-size: 14px;
        }
        #MainWidget{
            padding: 0 20px 10px 20px;
        }
        #Header {
            margin: 0 0 0 0;
            padding: 20px 20px 20px 20px;
            color: white;
            border: 1px solid gray;
            border-left: 0;
            border-right: 0;
            border-top: 0;
        }
        #Header QWidget {
            font-weight: bold;
            font-size: 25px;
        }
        #SubHeader {
            padding: 10px 0 10px 0;
            border: 1px solid gray;
            border-left: 0;
            border-right: 0;
            border-top: 0;
            margin: 0 0 10px 0;
        }
        #SubHeader QWidget {
            margin-bottom: 5px;
        }
        QComboBox {
            height: 25px;
            margin: 0 0 10px 0;
            padding: 2px 10px 2px 10px;
            border: 1px solid black;
            font-weight: bold;
            font-size: 18px;
        }
        QComboBox::drop-down {
            width: 25px;
            height: 2.1em;
        }
        QComboBox::down-arrow {
            color: blue;
        }
        #DeleteButton[enabled=true] {
            color: white;
            background-color: #cc2900;
        }
        #DeleteButton[enabled=false] {
            color: white;
            background-color: #ff8566;
        }
        #RetrieveButton[enabled=true] {
            color: white;
            background-color: #007acc;
        }
        #RetrieveButton[enabled=false] {
            color: white;
            background-color: #99d6ff;
        }
    """

    def __init__(self, model, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._model = model
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._setup_ui()
        self.setWindowTitle("Configuration Manager")
        self.setStyleSheet(ConfigurationManager.Stylesheet)

    def _setup_ui(self):
        self.setGeometry(0, 0, 1280, 800)
        self.main_widget = QFrame()
        self.main_widget.setObjectName('MainWidget')
        self.setCentralWidget(self.main_widget)
        self.layout = QGridLayout()
        self.main_widget.setLayout(self.layout)

        # Basic widgets
        self.editor = QTableView()
        self.delete_button = QPushButton('Delete', self)
        self.delete_button.setObjectName('DeleteButton')
        self.d_editor = QTableView()
        self.retrieve_button = QPushButton('Retrieve', self)
        self.retrieve_button.setObjectName('RetrieveButton')
        self.tree = QTreeView(self)
        self.config_type = QComboBox(parent=self)

        # Tab widgets
        self.tab1 = QWidget()
        self.tab1.layout = QVBoxLayout(self.tab1)
        self.tab2 = QWidget()
        self.tab2.layout = QVBoxLayout(self.tab2)
        self.tab1.layout.addWidget(self.editor)
        self.tab1.layout.addWidget(self.delete_button)
        self.tab2.layout.addWidget(self.d_editor)
        self.tab2.layout.addWidget(self.retrieve_button)

        self.editor_tab = QTabWidget(self)
        self.editor_tab.addTab(self.tab1, 'Configurations')
        self.editor_tab.addTab(self.tab2, 'Discarded Configurations')
        self.config_viewer = QWidget(self)
        self.config_viewer.layout = QVBoxLayout(self.config_viewer)
        self.config_viewer.layout.addWidget(self.editor_tab)
        self.config_viewer.layout.addWidget(self.tree)

        # Header widget
        self.header = QFrame(self)
        self.header.setObjectName('Header')
        self.header.layout = QHBoxLayout(self.header)
        self.header.layout.addStretch()
        self.header.layout.addWidget(
            QLabel('Configuration Database Manager', self.header))
        self.header.layout.addStretch()

        # Sub header with database genral information
        self.sub_header = QFrame(self)
        self.sub_header.setObjectName('SubHeader')
        self.sub_header.layout = QVBoxLayout(self.sub_header)

        self.server_layout = QHBoxLayout()
        self.server_layout.addWidget(QLabel('<b>Server:</b>', self.sub_header))
        self.server_layout.addWidget(QLabel(self._model.url, self.sub_header))
        self.server_layout.addStretch()

        self.size_layout = QHBoxLayout()
        self.size_layout.addWidget(QLabel('<b>DB Size:</b>', self.sub_header))
        request = self._model.query_db_size()
        if request['code'] == 200:
            dbsize = '{:.2f} MB'.format(request['result']['size']/(1024*1024))
        else:
            dbsize = 'Failed to retrieve information'
        self.size_layout.addWidget(QLabel(dbsize, self.sub_header))
        self.size_layout.addStretch()

        self.sub_header.layout.addLayout(self.server_layout)
        self.sub_header.layout.addLayout(self.size_layout)

        # Query form
        self.query_form = QFrame()
        self.query_form.setObjectName("QueryForm")
        self.query_form.layout = QVBoxLayout()
        self.query_form.setLayout(self.query_form.layout)

        self.configs_layout = QGridLayout()
        self.configs_layout.addWidget(QLabel('Configurations:', self), 0, 0)
        self.nr_configs = QLabel(self)
        self.configs_layout.addWidget(self.nr_configs, 0, 1)
        self.configs_layout.addWidget(QLabel('Discarded:', self), 0, 2)
        self.nr_discarded = QLabel(self)
        self.configs_layout.addWidget(self.nr_discarded, 0, 3)

        self.query_form.layout.addWidget(self.config_type)
        self.query_form.layout.addLayout(self.configs_layout)

        # Main widget layout setup
        self.layout.addWidget(self.header, 0, 0, 1, 3)
        self.layout.addWidget(self.sub_header, 1, 0, 1, 2, )
        self.layout.addWidget(self.query_form, 2, 0, 1, 2)
        self.layout.addWidget(self.config_viewer, 3, 0, 1, 2)
        self.layout.addWidget(self.tree, 1, 2, 4, 1)
        # self.layout.addWidget(self.delete_button, 4, 0, 1, 2)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 2)
        self.layout.setColumnStretch(2, 2)

        # Set table models and options
        self.editor_model = ConfigDbTableModel('', self._model)
        self.d_editor_model = ConfigDbTableModel('', self._model, True)
        self.editor.setModel(self.editor_model)
        self.editor.setSelectionBehavior(self.editor.SelectRows)
        self.editor.setSortingEnabled(True)
        self.editor.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.d_editor.setModel(self.d_editor_model)
        self.d_editor.setSelectionBehavior(self.editor.SelectRows)
        self.d_editor.setSortingEnabled(True)
        self.d_editor.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.d_editor.setSelectionMode(self.d_editor.SingleSelection)
        # Set tree model and options
        self.tree_model = JsonTreeModel(None, None, self._model)
        self.tree.setModel(self.tree_model)
        # Delete button
        self.delete_button.setEnabled(False)
        self.retrieve_button.setEnabled(False)

        # Get configuration types
        request = self._model.get_types()
        if request['code'] == 200:
            types = request['result']
            self.config_type.addItem('Select a configuration type...')
            self.config_type.addItems(types)
        else:
            self._logger.warning('No configuration found')
            self.config_type.addItem('No configuration found...')

        # Signals and slots

        # Tab
        self.editor_tab.currentChanged.connect(self._tab_changed)
        # Fill tables when configuration is selected
        self.config_type.currentTextChanged.connect(self._fill_table)
        # Fill tree when a configuration is selected
        self.editor.selectionModel().selectionChanged.connect(
            lambda x, y: self._fill_tree())
        self.d_editor.selectionModel().selectionChanged.connect(
            lambda x, y: self._fill_tree())
        # Connect database error to slot that show messages
        self.editor_model.connectionError.connect(self._database_error)
        self.d_editor_model.connectionError.connect(self._database_error)
        # Makes tree column extend automatically to show content
        self.tree.expanded.connect(
            lambda idx: self.tree.resizeColumnToContents(idx.column()))
        # Button action
        self.delete_button.pressed.connect(self._remove_configuration)
        self.retrieve_button.pressed.connect(self._retrieve_configuration)
        # Set constants
        ConfigurationManager.NAME_COL = \
            self.editor_model.horizontalHeader.index('name')
        ConfigurationManager.CONFIG_TYPE_COL = \
            self.editor_model.horizontalHeader.index('config_type')

        self.editor.resizeColumnsToContents()
        self.d_editor.resizeColumnsToContents()

    @pyqtSlot(str)
    def _fill_table(self, config_type):
        """Fill table with configuration of `config_type`."""
        request = self._model.find_nr_configs(
            config_type=config_type, discarded=None)
        if request['code'] == 200:
            self.nr_configs.setText(str(request['result']))
        request = self._model.find_nr_configs(
            config_type=config_type, discarded=True)
        if request['code'] == 200:
            self.nr_discarded.setText(str(request['result']))

        self.editor_model.setupModelData(config_type)
        self.d_editor_model.setupModelData(config_type)
        self.editor.resizeColumnsToContents()
        self.d_editor.resizeColumnsToContents()

    @pyqtSlot()
    def _fill_tree(self):
        if self.editor_tab.currentIndex() == 0:
            configs = list()
            rows = self._get_selected_rows(self.editor)
            # Get selected rows
            for row in rows:
                # Get name and configuration type
                configs.append(self._type_name(row, self.editor_model))
            # Set tree data
            self.tree_model.setupModelData(configs)
            if len(configs) == 1:
                self.delete_button.setEnabled(True)
                self.delete_button.setText(
                    'Delete {} ({})'.format(configs[0][1], configs[0][0]))

            elif len(configs) > 1:
                self.delete_button.setEnabled(True)
                self.delete_button.setText(
                    'Delete {} configurations'.format(len(configs)))
            else:
                self.delete_button.setEnabled(False)
            self.delete_button.style().polish(self.delete_button)
        else:
            try:
                row = self._get_selected_rows(self.d_editor).pop()
            except KeyError:
                self.retrieve_button.setEnabled(False)
                self.retrieve_button.style().polish(self.retrieve_button)
            else:
                config_type, name = self._type_name(row, self.d_editor_model)
                self.tree_model.setupModelData([(config_type, name)])
                self.retrieve_button.setEnabled(True)
                self.retrieve_button.style().polish(self.retrieve_button)
        # self.tree.resizeColumnsToContents()

    @pyqtSlot()
    def _remove_configuration(self):
        type = QMessageBox.Question
        title = 'Remove configuration?'
        buttons = QMessageBox.Ok | QMessageBox.Cancel

        # self.editor.selectRow(index.row())
        rows = list(self._get_selected_rows(self.editor))
        message = 'Remove configurations:\n'
        for row in rows:
            config_type = self.editor_model.createIndex(row, 0).data()
            name = self.editor_model.createIndex(row, 1).data()
            message += '- {} ({})\n'.format(name, config_type)

        msg = QMessageBox(type, title, message, buttons).exec_()
        if msg == QMessageBox.Ok:
            rows.sort(reverse=True)
            for row in rows:
                self.editor_model.removeRows(row)

        self.editor.selectionModel().clearSelection()
        self._fill_table(self.config_type.currentText())

    @pyqtSlot()
    def _retrieve_configuration(self):
        type = QMessageBox.Question
        title = 'Retrieve configuration?'
        buttons = QMessageBox.Ok | QMessageBox.Cancel

        try:
            row = self._get_selected_rows(self.d_editor).pop()
        except KeyError:
            pass
        else:
            config_type, name = self._type_name(row, self.d_editor_model)
            name = name[:-37]
            message = \
                'Retrieve configuration {} ({})?'.format(config_type, name)
            msg = QMessageBox(type, title, message, buttons).exec_()
            if msg == QMessageBox.Ok:
                try:
                    self.d_editor_model.removeRows(row)
                except TypeError:
                    self._database_error(
                        'Exception',
                        'Configuration no longer is in the correct format',
                        'retrieve configuration')

        self.editor.selectionModel().clearSelection()
        self._fill_table(self.config_type.currentText())

    @pyqtSlot(int)
    def _tab_changed(self, index):
        if index == 0:
            self.editor.selectionModel().clearSelection()
            self.delete_button.setText('Delete')
            self.delete_button.setEnabled(False)
            self.delete_button.style().polish(self.delete_button)
        else:
            self.d_editor.selectionModel().clearSelection()
            self.retrieve_button.setEnabled(False)
            self.retrieve_button.style().polish(self.retrieve_button)
        self.tree_model.setupModelData([])

    @pyqtSlot(int, str, str)
    def _database_error(self, code, message, operation):
        type = QMessageBox.Warning
        title = 'Something went wrong'
        msg = '{}: {}, while trying to {}'.format(code, message, operation)
        QMessageBox(type, title, msg).exec_()

    def _get_selected_rows(self, table):
        index_list = table.selectionModel().selectedIndexes()
        return {idx.row() for idx in index_list}

    def _type_name(self, row, model):
        # Return config_type and name given a row and a table model
        return (model.createIndex(row, self.CONFIG_TYPE_COL).data(),
                model.createIndex(row, self.NAME_COL).data())
