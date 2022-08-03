"""Defines PyDM widget with a spinbox and a scrollbar."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QSizePolicy as QSzPol
from .spinbox import SiriusSpinbox
from .scrollbar import PyDMScrollBar


class PyDMSpinboxScrollbar(QWidget):
    """Composition of a Spinbox and a Scrollbar to set a float PV."""

    def __init__(self, parent=None, init_channel=None):
        """Init."""
        super().__init__(parent)
        self._init_channel = init_channel

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.spinbox = SiriusSpinbox(
            parent=self, init_channel=init_channel)
        self.spinbox.setAlignment(Qt.AlignCenter)
        self.spinbox.showStepExponent = False
        self.spinbox.setStyleSheet("SiriusSpinbox{min-height:1.29em;}")
        self.spinbox.setSizePolicy(QSzPol.Expanding, QSzPol.Preferred)

        self.scrollbar = PyDMScrollBar(
            parent=self, init_channel=init_channel)
        self.scrollbar.wheelEvent = lambda event: event.ignore()
        self.scrollbar.setTracking(False)
        self.scrollbar.setStyleSheet("PyDMScrollBar{max-height:0.7em;}")

        layout.addWidget(self.spinbox, 0, 0, 2, 1)
        layout.addWidget(self.scrollbar, 2, 0, 1, 1)
