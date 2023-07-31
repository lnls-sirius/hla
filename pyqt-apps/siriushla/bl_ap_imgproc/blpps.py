"""Beamline-specific classes."""

from siriuspy.devices import BLPPSCtrl as _BLPPSCtrl


class BLPPS:
    """."""

    def __init__(self, device):
        """Init."""
        if 'CAX' in device:
            self.pps = _BLPPSCtrl(_BLPPSCtrl.DEVICES.CAX)
        else:
            self.pss = None

    def beamline_open(self):
        if self.pss:
            return self.pss.cmd_beamline_open()
        else:
            return True

