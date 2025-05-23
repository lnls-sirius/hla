from qtpy.QtWidgets import QFrame, QHBoxLayout, QWidget
from siriushla.widgets import SiriusPushButton

from .util import SYSTEM_COLORS


class RFEnblDsblButton(QWidget):
    """Button to enbl/dsbl attribute controlled by 2 PVs."""

    def __init__(self, parent=None, channels=dict()):
        super().__init__(parent)
        self.pb_off = SiriusPushButton(
            parent=self, label='Off', init_channel=channels['off'],
            releaseValue=0)
        self.pb_off.setStyleSheet('min-width:1.4em; max-width:1.4em;')
        self.pb_on = SiriusPushButton(
            parent=self, label='On', init_channel=channels['on'],
            releaseValue=0)
        self.pb_on.setStyleSheet('min-width:1.4em; max-width:1.4em;')
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        lay.addStretch()
        lay.addWidget(self.pb_off)
        lay.addWidget(self.pb_on)
        lay.addStretch()


class RFTitleFrame(QFrame):
    """QFrame with background color set depending on the specific system."""

    def __init__(self, parent=None, system=''):
        super().__init__(parent)
        if system != '':
            self.setStyleSheet(f'background-color: {SYSTEM_COLORS[system]};')
