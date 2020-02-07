"""List with power supplies cycling status."""
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QListView, QApplication, QDialog, QVBoxLayout, \
    QLabel, QPushButton
from qtpy.QtGui import QStandardItemModel, QStandardItem

from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow


class PSList(QListView):
    """PS List."""

    def __init__(self, pwrsupplies=set(), parent=None):
        """Constructor."""
        super().__init__(parent)
        self._pwrsupplies = pwrsupplies
        self._model = None
        self._setup_ui()
        self.doubleClicked.connect(self._open_detail)

    @property
    def pwrsupplies(self):
        """List items."""
        return self._pwrsupplies

    @pwrsupplies.setter
    def pwrsupplies(self, pwrsupplies):
        self._pwrsupplies = pwrsupplies
        self._setup_ui()

    def _setup_ui(self):
        self._model = QStandardItemModel(self)
        for ps in self._pwrsupplies:
            text = QStandardItem()
            text.setData(ps, Qt.DisplayRole)
            self._model.appendRow(text)

        self.setModel(self._model)

    def _open_detail(self, index):
        app = QApplication.instance()
        psname = index.data()
        app.open_window(PSDetailWindow, parent=self, **{'psname': psname})


class PSStatusDialog(QDialog):
    """Dialog to show list of pwrsupplies not ok."""

    def __init__(self, pwrsupplies=set(), text='', parent=None):
        super().__init__(parent)
        self.pwrsupplies = pwrsupplies
        self.text = text
        self._setup_ui()

    def _setup_ui(self):
        label = QLabel(self.text, self)
        self._status_list = PSList(self.pwrsupplies, self)
        self._ok_bt = QPushButton('Ok', self)
        self._ok_bt.clicked.connect(self.close)

        lay = QVBoxLayout()
        lay.addWidget(label)
        lay.addWidget(self._status_list)
        lay.addWidget(self._ok_bt)
        self.setLayout(lay)
