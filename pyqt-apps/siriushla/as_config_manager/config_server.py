"""Window to manage configurations."""
import logging
# import json

from pydm.PyQt.QtGui import QWidget, QLabel, QGridLayout, QComboBox, \
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem
from pydm.PyQt.QtCore import pyqtSlot

from siriuspy.servconf.conf_service import ConfigService


c = ConfigService('http://127.0.0.1').get_config('bo_normalized', 'config_a')


class ConfigurationManager(QWidget):
    """."""

    def __init__(self, model, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._model = model
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        # Widgets
        self.editor = QTableWidget(0, 3, self)
        self.editor.setHorizontalHeaderLabels(
            ['Name', 'Created', 'Modifications'])
        self.editor.setSelectionBehavior(QTableWidget.SelectRows)
        self.editor.itemClicked.connect(self._item_clicked)
        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['Key', 'Value'])
        self.config_type = QComboBox(parent=self)

        self.layout.addWidget(self.config_type, 0, 0, 1, 2)
        self.layout.addWidget(self.editor, 1, 0)
        self.layout.addWidget(self.tree, 1, 1)

        # Get configuration types
        request = self._model.get_types()
        if request['code'] == 200:
            types = request['result']
            self.config_type.addItem('Select a configuration type...')
            self.config_type.addItems(types)
        else:
            self._logger.warning('No configuration found')
            self.config_type.addItem('No configuration found...')

        self.config_type.currentTextChanged.connect(self.fillTable)

    def fillTable(self, config_type):
        """Fill table with configuration of `config_type`."""
        request = self._model.find_configs(config_type=config_type)
        if request['code'] == 200:
            configs = request['result']
            if configs:
                self.editor.setRowCount(len(configs))
                for line, config in enumerate(configs):
                    self.editor.setItem(
                        line, 0, QTableWidgetItem(config['name']))
                    self.editor.setItem(
                        line, 1,
                        QTableWidgetItem(self._model.conv_timestamp_flt_2_txt(
                            config['created'])))
                    self.editor.setItem(
                        line, 2,
                        QTableWidgetItem(str(len(config['modified']))))
                self.editor.resizeColumnsToContents()
                self._item_clicked(self.editor.item(0, 0))
        else:
            pass

    def fillTree(self, config):
        """Fill tree."""
        # Clear tree
        self.tree.clear()
        # Fill tree
        self.addChildren(
            self.tree.invisibleRootItem(), config)

    def addChildren(self, item, config):
        """Add children."""
        if isinstance(config, dict):
            for key, val in config.items():
                if isinstance(val, (list, dict)):  # Has children
                    new_item = QTreeWidgetItem([key, ''])
                    self.addChildren(new_item, val)
                    item.addChild(new_item)
                else:
                    item.addChild(QTreeWidgetItem([key, str(val)]))
        elif isinstance(config, list):
            for idx, value in enumerate(config):
                if isinstance(value, (list, dict)):  # Has children
                    new_item = QTreeWidgetItem([str(idx), ''])
                    self.addChildren(new_item, value)
                    item.addChild(new_item)
                else:
                    item.addChild(QTreeWidgetItem([str(idx), str(value)]))

        # for idx, child in enumerate(children):
        #     if isinstance(child, int):
        #         item.addChild(tree_items[child])
        #     else:
        #         self.addChildren(
        #             tree_items[children[idx - 1]], child, tree_items)

    @pyqtSlot(QTableWidgetItem)
    def _item_clicked(self, item):
        config_type = self.config_type.currentText()
        name = self.editor.item(item.row(), 0).text()
        request = self._model.get_config(config_type, name)
        if request['code'] == 200:
            self.fillTree(request['result'])
        else:
            print('error {}, {}'.format(config_type, name))


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication
    app = SiriusApplication()
    model = ConfigService('http://127.0.0.1')
    widget = ConfigurationManager(model)
    widget.show()
    sys.exit(app.exec_())
