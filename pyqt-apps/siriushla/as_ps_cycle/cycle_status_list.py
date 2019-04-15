"""List with magnet cycling status."""
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QListView, QApplication
from qtpy.QtGui import QStandardItemModel, QStandardItem

from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow


class CycleStatusList(QListView):
    """Magnet cycling status list."""

    # OK = QIcon('icons8-checkmark.svg')
    # NOK = QIcon('icons8-delete.svg')

    def __init__(self, magnets=list(), parent=None):
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
            # text.setData(CycleStatusList.NOK, Qt.DecorationRole)
            self._model.appendRow(text)

        self.setModel(self._model)

    def _open_detail(self, index):
        app = QApplication.instance()
        maname = index.data()
        app.open_window(PSDetailWindow, parent=self, **{'psname': maname})
