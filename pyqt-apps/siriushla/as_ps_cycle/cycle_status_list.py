"""List with magnet cycling status."""
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QListView, QApplication, QDialog, QVBoxLayout, \
    QLabel, QPushButton
from qtpy.QtGui import QStandardItemModel, QStandardItem

from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow


class MagnetsList(QListView):
    """Magnets List."""

    def __init__(self, magnets=set(), parent=None):
        """Constructor."""
        super().__init__(parent)
        self._magnets = magnets
        self._model = None
        self._setup_ui()
        self.doubleClicked.connect(self._open_detail)

    @property
    def magnets(self):
        """List items."""
        return self._magnets

    @magnets.setter
    def magnets(self, magnets):
        self._magnets = magnets
        self._setup_ui()

    def _setup_ui(self):
        self._model = QStandardItemModel(self)
        for magnet in self._magnets:
            text = QStandardItem()
            text.setData(magnet, Qt.DisplayRole)
            self._model.appendRow(text)

        self.setModel(self._model)

    def _open_detail(self, index):
        app = QApplication.instance()
        maname = index.data()
        if 'LI' in maname:
            return
        app.open_window(PSDetailWindow, parent=self, **{'psname': maname})


class MagnetsListDialog(QDialog):
    """Dialog to show list of magnets not ok."""

    def __init__(self, magnets=set(), text='', parent=None):
        super().__init__(parent)
        self.magnets = magnets
        self.text = text
        self._setup_ui()

    def _setup_ui(self):
        label = QLabel(self.text, self)
        self._status_list = MagnetsList(self.magnets, self)
        self._ok_bt = QPushButton('Ok', self)
        self._ok_bt.clicked.connect(self.close)

        lay = QVBoxLayout()
        lay.addWidget(label)
        lay.addWidget(self._status_list)
        lay.addWidget(self._ok_bt)
        self.setLayout(lay)
