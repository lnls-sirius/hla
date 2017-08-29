"""Defines PyDM widget with a line edit and a double scrollbar."""
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QStyle, QStyleOption, \
    QPainter
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.scrollbar import PyDMScrollBar


class FloatSetPointWidget(QWidget):
    """Widget to set the setpoint of a float PV."""

    def __init__(self, channel, parent=None):
        """Constructor sets channel name."""
        super().__init__(parent)
        self._channel = channel
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.sp_lineedit = PyDMLineEdit(
            parent=self, init_channel=self._channel)
        # self.sp_lineedit.setObjectName("lineedit")
        self.sp_scrollbar = PyDMScrollBar(
            parent=self, init_channel=self._channel)
        self.sp_scrollbar.setMouseTracking(False)
        # self.tension_sp_scrollbar.setObjectName("scrollbar")
        self.layout.addWidget(self.sp_lineedit)
        self.layout.addWidget(self.sp_scrollbar)
        self.setLayout(self.layout)

    def set_limits_from_pv(self, value):
        """Set wether to use limiits from the pv channel."""
        self.sp_scrollbar.limitsFromPV = value

    def paintEvent(self, event):
        """Need to override paintEvent in order to apply CSS."""
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
