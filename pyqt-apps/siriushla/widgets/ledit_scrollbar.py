"""Defines PyDM widget with a line edit and a double scrollbar."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QStyle, QStyleOption, \
    QSizePolicy as QSzPol
from qtpy.QtGui import QPainter
from .scrollbar import PyDMScrollBar
from .line_edit import SiriusLineEdit


class PyDMLinEditScrollbar(QWidget):
    """Composition of a LineEdit and a Scrollbar to set a float PV."""

    def __init__(self, parent=None, init_channel=None):
        """Init."""
        super().__init__(parent)
        self._init_channel = init_channel

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.lineedit = SiriusLineEdit(
            parent=self, init_channel=init_channel)
        self.lineedit.setAlignment(Qt.AlignCenter)
        self.lineedit.setStyleSheet("SiriusLineEdit{min-height:1.29em;}")
        self.lineedit.setSizePolicy(QSzPol.Expanding, QSzPol.Preferred)

        self.scrollbar = PyDMScrollBar(
            parent=self, init_channel=init_channel)
        self.scrollbar.wheelEvent = lambda event: event.ignore()
        self.scrollbar.setTracking(False)
        self.scrollbar.setStyleSheet("PyDMScrollBar{max-height:0.7em;}")

        layout.addWidget(self.lineedit, 0, 0, 2, 1)
        layout.addWidget(self.scrollbar, 2, 0, 1, 1)

    def paintEvent(self, event):
        """Need to override paintEvent in order to apply CSS."""
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
