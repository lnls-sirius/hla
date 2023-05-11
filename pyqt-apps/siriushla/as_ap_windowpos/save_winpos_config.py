"""Interface to handle main operation commands."""

import qtawesome as qta

import json

from socket import gethostname

from qtpy.QtGui import QKeySequence, QKeyEvent

from qtpy.QtCore import Qt, Slot, Signal, QEvent, QModelIndex
from qtpy.QtWidgets import QWidget, QPushButton, QVBoxLayout, QApplication, \
    QMessageBox, QTableView, QHeaderView, QTableWidget, QLineEdit, QCheckBox, \
    QTableWidgetItem

from siriuspy.envars import VACA_PREFIX

from siriushla.widgets import SiriusMainWindow

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.util import get_appropriate_color

from models import WinPosTableModel as _WinPosTableModel

from util import WinInfoPos as _WinInfoPos

from util import get_win_info

from datetime import datetime


class _CustomTable(QTableWidget):

    def __init__(self, rows, columns):
        super(_CustomTable, self).__init__()
        self.rows = rows
        self.columns = columns
        self.buildtable()

    def keyPressEvent(self, event):
        if event.type() == QKeyEvent.KeyPress:
            if event.matches(QKeySequence.Copy):
                indexes = self.selectionModel().selectedIndexes()
                if len(indexes) == 1:
                    index = indexes[0]
                    if index.column() == 2:
                        value = self.model().data(index)
                        QApplication.instance().clipboard().setText(str(value))
                else:
                    QMessageBox.information(
                        self, 'Copy', 'No support for multi-cell copying')
            elif event.matches(QKeySequence.Paste):
                value = QApplication.instance().clipboard().text()
                indexes = self.selectionModel().selectedIndexes()
                for index in indexes:
                    self.pasteDelay(index, value)

    def pasteDelay(self, index, value):
        if index.column() != 2:
            return
        try:
            value = float(value)
        except ValueError:
            return
        self.model().setData(index, value)

    def buildtable(self):
        for i in range(self.rows):
            self.insertRow(i)
        for i in range(self.columns):
            self.insertColumn(i)
            self.horizontalHeader().setSectionResizeMode(i,
            QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0,
            QHeaderView.ResizeToContents)

class WinPosSave(SiriusMainWindow):
    """Window Position Save Configuration window."""

    def __init__(self, client=None, parent=None, prefix=VACA_PREFIX):
        """Init."""
        super().__init__(parent)
        self._client = client

        self.setObjectName('WinPos')
        self.setWindowTitle('Window Position Configuration')
        self._setup_ui()
        self._central_widget.setStyleSheet("""
            #CentralWidget {
                min-width: 40em;
                min-height: 40em;
            }
        """)

    def _setup_ui(self):
        # Set central widget
        self._central_widget = QWidget()
        self._central_widget.setObjectName('CentralWidget')
        self._central_widget.layout = QVBoxLayout()
        self._central_widget.setLayout(self._central_widget.layout)
        self.setCentralWidget(self._central_widget)

        # Add name of the file field
        self.namebox = QLineEdit(self)
        self.namebox.setObjectName('namebox')
        self.namebox.setToolTip('Enter the filename to save to file')
        self.namebox.setPlaceholderText('Enter the filename to save to file')
        self.namebox.adjustSize()

        # Add configuration table
        aux = get_win_info()
        open_wins = []
        for u in aux:
            open_wins.append(u['window'])
        open_wins = list(dict.fromkeys(open_wins))
        headers = ['Select', 'Window', 'Size', 'Position']
        self._table = _CustomTable(len(open_wins), len(headers))
        self._table.setObjectName('options_tbl')
        self._table.setHorizontalHeaderLabels(headers)
        for row in range(self._table.rowCount()):
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Checked)
            checkbox.setStyleSheet("margin-left:50%; margin-right:50%")
            self._table.setCellWidget(row, 0, checkbox)
            _window = open_wins[row]
            wid_item = QTableWidgetItem(_window)
            self._table.setItem(row-1, len(headers)+1, wid_item)
        self._table.setSortingEnabled(True)
        self._table.setSelectionBehavior(QTableView.SelectRows)

        # Add Save Button
        self._save_btn = QPushButton('Save', self)
        self._save_btn.setObjectName('save_btn')
        self._save_btn.setEnabled(True)

        # Add widgets
        self._central_widget.layout.addWidget(self.namebox)
        self._central_widget.layout.addWidget(self._table)
        self._central_widget.layout.addWidget(self._save_btn)

        # Add signals
        self._save_btn.clicked.connect(self._save)

    def _write_file(self, file):
        # Save file to file server
        print(file)

    @Slot()
    def _save(self):
        # Save button def
        selected = self._table.
        if self.namebox.text() != '':
            configdict = dict.fromkeys(['name',
                                        'created',
                                        'modified',
                                        'computer',
                                        'config'])
            configdict['name'] = self.namebox.text()
            epoch = datetime.utcfromtimestamp(0)
            configdict['created'] = (datetime.now()-epoch).total_seconds()*1000
            configdict['modified'] = configdict['created']
            configdict['computer'] = gethostname()
            configdict['config'] = get_win_info()
            self._write_file(configdict)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Warning')
            msg.setInformativeText('More information')
            msg.setWindowTitle('Warning')
            msg.information(self, 'Warning!', 'Set the filename!')


    # def _is_configuration_valid(self):
    #     if self._table.model().model_data:
    #         self._config_valid = True
    #     else:
    #         self._config_valid = False
    #     self._load_btn.setEnabled(self._config_valid)

app = SiriusApplication()
app.open_window(WinPosSave, parent=None)
sys.exit(app.exec_())
