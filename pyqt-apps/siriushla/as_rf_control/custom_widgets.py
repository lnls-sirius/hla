

from qtpy.QtWidgets import QHBoxLayout, QWidget
from pydm.widgets import PyDMPushButton


class RFEnblDsblButton(QWidget):
    """Button to enbl/dsbl attribute controlled by 2 PVs."""

    def __init__(self, parent=None, channels=dict()):
        """Init."""
        super().__init__(parent)
        self.pb_off = PyDMPushButton(
            parent=self, label='Off', init_channel=channels['off'],
            pressValue=1, releaseValue=0)
        self.pb_off.writeWhenRelease = True
        self.pb_off.setStyleSheet('min-width:1.4em; max-width:1.4em;')
        self.pb_on = PyDMPushButton(
            parent=self, label='On', init_channel=channels['on'],
            pressValue=1, releaseValue=0)
        self.pb_on.writeWhenRelease = True
        self.pb_on.setStyleSheet('min-width:1.4em; max-width:1.4em;')
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        lay.addStretch()
        lay.addWidget(self.pb_off)
        lay.addWidget(self.pb_on)
        lay.addStretch()
