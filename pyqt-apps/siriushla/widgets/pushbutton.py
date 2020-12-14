"""Sirius pushbutton."""

from functools import partial as _part
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QPushButton
from pydm.widgets.base import PyDMWritableWidget


class SiriusPushButton(PyDMWritableWidget, QPushButton):
    """A simple pushbutton with pressed and released signals."""

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
