"""Booster Ramp Control HLA: Ramp Statistics Module."""

from PyQt5.QtWidgets import QGroupBox
from siriuspy.namesys import SiriusPVName as _PVName


class RampStatistics(QGroupBox):
    """Widget to ramp status monitoring."""

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('Statistics', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()

    def _setupUi(self):
        pass
