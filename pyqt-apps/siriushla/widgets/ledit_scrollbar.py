"""Defines PyDM widget with a line edit and a double scrollbar."""
from qtpy.QtWidgets import QWidget, QVBoxLayout, QStyle, QStyleOption
from qtpy.QtGui import QPainter
from pydm.widgets.line_edit import PyDMLineEdit
from siriushla.widgets.scrollbar import PyDMScrollBar
from siriushla.widgets.line_edit import SiriusLineEdit


class PyDMLinEditScrollbar(QWidget):
    """Widget to set the setpoint of a float PV."""

    def __init__(self, channel, parent=None):
        """Constructor sets channel name."""
        super().__init__(parent)
        self._channel = channel
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.sp_lineedit = SiriusLineEdit(
            parent=self, init_channel=self._channel)
        self.sp_lineedit.showUnits = True
        self.sp_scrollbar = PyDMScrollBar(
            parent=self, init_channel=self._channel)
        self.sp_scrollbar.wheelEvent = lambda event: event.ignore()
        self.layout.addWidget(self.sp_lineedit)
        self.layout.addWidget(self.sp_scrollbar)
        self.setLayout(self.layout)


    def paintEvent(self, event):
        """Need to override paintEvent in order to apply CSS."""
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
