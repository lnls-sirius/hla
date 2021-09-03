"""Wait dialog."""

import time as _time

from qtpy.QtCore import Signal, Slot, QThread
from qtpy.QtWidgets import QVBoxLayout, QPushButton

import qtawesome as qta

from ..windows import SiriusDialog


class WaitDialog(SiriusDialog):
    """Wait Dialog."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Wait')
        self.wait_symbol = QPushButton(self)
        self.wait_symbol.setFlat(True)
        spin_icon = qta.icon(
            'fa5s.spinner', animation=qta.Spin(self.wait_symbol))
        self.wait_symbol.setIcon(spin_icon)
        lay = QVBoxLayout(self)
        lay.addWidget(self.wait_symbol)


class WaitThread(QThread):

    opendiag = Signal()
    closediag = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._quit_task = False

    @Slot()
    def exit_task(self):
        """Set quit flag."""
        self._quit_task = True

    def run(self):
        self.opendiag.emit()
        while not self._quit_task:
            _time.sleep(0.1)
        self.closediag.emit()
