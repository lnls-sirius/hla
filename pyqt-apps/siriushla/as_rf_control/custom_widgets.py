from functools import partial as _part
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QHBoxLayout, QWidget, QPushButton
from pydm.widgets.base import PyDMWritableWidget


class RFEnblDsblButton(QWidget):
    """Button to enbl/dsbl attribute controlled by 2 PVs."""

    def __init__(self, parent=None, channels=dict()):
        super().__init__(parent)
        self.pb_off = RFPushButton(
            parent=self, label='Off', init_channel=channels['off'])
        self.pb_off.setStyleSheet('min-width:1.4em; max-width:1.4em;')
        self.pb_on = RFPushButton(
            parent=self, label='On', init_channel=channels['on'])
        self.pb_on.setStyleSheet('min-width:1.4em; max-width:1.4em;')
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        lay.addStretch()
        lay.addWidget(self.pb_off)
        lay.addWidget(self.pb_on)
        lay.addStretch()


class RFPushButton(PyDMWritableWidget, QPushButton):

    def __init__(self, parent=None, init_channel=None, label='', icon=None,
                 pressValue=1, releaseValue=0):
        if not icon:
            QPushButton.__init__(self, label, parent)
        else:
            QPushButton.__init__(self, icon, label, parent)
        PyDMWritableWidget.__init__(self, init_channel=init_channel)
        self._alarm_sensitive_border = False
        self.pressValue = pressValue
        self.releaseValue = releaseValue
        self.pressed.connect(_part(self.sendValue, self.pressValue))
        self.released.connect(_part(self.sendValue, self.releaseValue))

    @Slot()
    def sendValue(self, value):
        """Send value."""
        self.send_value_signal[self.channeltype].emit(
            self.channeltype(value))
