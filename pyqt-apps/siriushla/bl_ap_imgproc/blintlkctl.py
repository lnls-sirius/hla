"""Beamline-specific classes."""

from siriuspy.devices import ASMPSCtrl as _ASMPSCtrl
from siriuspy.devices import BLInterlockCtrl as _BLInterlockCtrl


class BLIntckCtrl:
    """."""

    def __init__(self, device):
        """Init."""
        if 'CAX' in device:
            self.blintlk = _BLInterlockCtrl(_BLInterlockCtrl.DEVICES.CAX)
            self.mps = _ASMPSCtrl()
        else:
            self.blintlk = None
            self.mps = None

    @property
    def beamline_opened(self):
        """."""
        if self.blintlk and self.blintlk.connected:
            return self.blintlk.is_beamline_opened
        else:
            return 2

    def gamma_enable(self):
        """."""
        if self.mps and self.mps.connected:
            return self.mps.cmd_gamma_enable()
        else:
            return False

    def beamline_open(self):
        """."""
        if self.blintlk and self.blintlk.connected:
            return self.blintlk.cmd_beamline_open()
        else:
            return False
