"""Interface to handle main operation commands."""

import qtawesome as qta

import json

from socket import gethostname

from qtpy.QtGui import QKeySequence, QKeyEvent

from qtpy.QtCore import Qt, Slot, Signal, QEvent, QModelIndex
from qtpy.QtWidgets import QWidget, QPushButton, QVBoxLayout, QApplication, \
    QMessageBox, QTableView, QHeaderView, QTableWidget

from siriuspy.envars import VACA_PREFIX

from siriushla.widgets import SiriusMainWindow

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.util import get_appropriate_color

from models import WinPosTableModel as _WinPosTableModel

from util import open_window_args as _open_window
from util import WinInfoPos as _WinInfoPos

class _CustomTable(QTableView):

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


class WinPosLoad(SiriusMainWindow):
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

    def on_selection_changed(self):
        self._load_btn.setEnabled(
            bool(self._table.selectionModel().selectedRows())
        )

    def _setup_ui(self):
        # Set central widget
        self._central_widget = QWidget()
        self._central_widget.setObjectName('CentralWidget')
        self._central_widget.layout = QVBoxLayout()
        self._central_widget.setLayout(self._central_widget.layout)
        self.setCentralWidget(self._central_widget)

        # Add configuration table
        self._table = _CustomTable(self)
        self._table.setObjectName('config_tbl')
        address = 'pyqt-apps/siriushla/as_ap_windowpos/database/config.json'
        with open(address) as f:
            data = json.load(f)
        self._table.setModel(_WinPosTableModel(configs=data))
        self._table.horizontalHeader().setSectionResizeMode(0,
            QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1,
            QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2,
            QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3,
            QHeaderView.ResizeToContents)
        self._table.setSortingEnabled(True)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        # self._table.setItemDelegate(PVConfigurationDelegate())

        # Add Read Button
        self._load_btn = QPushButton('Load', self)
        self._load_btn.setObjectName('load')
        self._load_btn.setEnabled(False)

        # # Add Save Button
        # self._save_btn = QPushButton('Save', self)
        # self._save_btn.setObjectName('save_btn')
        # self._save_btn.setEnabled(False)

        # Add widgets
        # self._central_widget.layout.addWidget(self._name_le)
        self._central_widget.layout.addWidget(self._table)
        # self._central_widget.layout.addWidget(self._save_btn)
        self._central_widget.layout.addWidget(self._load_btn)
        # self._is_configuration_valid()

        # Add signals
        # self._type_cb.currentTextChanged.connect(self._fill_table)
        self._load_btn.clicked.connect(self._load)
        self._load_btn.setEnabled(False)
        # self._save_btn.clicked.connect(self._save)

        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.selectionModel().selectionChanged.connect(
            self.on_selection_changed)
        self.on_selection_changed()

    @Slot()
    def _load(self):
        failed_items = []
        hostname = gethostname()
        idx_row = self._table.currentIndex().row()
        idx = self._table.model().index(idx_row, 0)
        config_data = self._table.model().data(idx, config=True)
        if config_data['computer'] == hostname:
            # print(config_data["config"])
            _open_window(config_data["config"])
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Warning')
            msg.setInformativeText('More information')
            msg.setWindowTitle('Warning')
            ans = msg.question(self, 'Confirm?', 'This configuration belongs to another computer, are you sure you want to open it?', msg.Yes, msg.No)
            if ans == msg.Yes:
                _open_window(config_data["config"])
            else:
                msg.information(self, 'Aborted!', 'Operation aborted!')



    # def _is_configuration_valid(self):
    #     if self._table.model().model_data:
    #         self._config_valid = True
    #     else:
    #         self._config_valid = False
    #     self._load_btn.setEnabled(self._config_valid)

app = SiriusApplication()
app.open_window(WinPosLoad, parent=None)
sys.exit(app.exec_())
