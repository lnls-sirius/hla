"""Custom widgets."""

import numpy as np

from qtpy.QtCore import Qt, Slot

from pydm.widgets import PyDMLineEdit
from pydm.widgets.waveformplot import WaveformCurveItem

from ..as_ap_configdb import LoadConfigDialog as _LoadConfigDialog


class ConfigLineEdit(PyDMLineEdit):
    """Configuration line edit."""

    def mouseReleaseEvent(self, _):
        """Reimplement mouseReleaseEvent."""
        config_type = 'si_idff'
        popup = _LoadConfigDialog(config_type)
        popup.configname.connect(self._config_changed)
        popup.exec_()

    def _config_changed(self, configname):
        self.setText(configname)
        self.send_value()
        self.value_changed(configname)


class SectionedWaveformCurveItem(WaveformCurveItem):

    GAP_MIN = 0  # [mm]
    GAP_MAX = 24  # [mm]

    def __init__(self, section, **kwargs):
        super().__init__(**kwargs)
        self.section = section

    @Slot(np.ndarray)
    def receiveYWaveform(self, new_waveform):
        size = len(new_waveform)/4
        min = int(size*self.section)
        max = int(size*(self.section+1))
        ydata = new_waveform[min:max]
        npts = len(ydata)
        xdata = self.GAP_MIN + (self.GAP_MAX - self.GAP_MIN) * np.arange(0, npts) / (npts - 1)
        super().receiveXWaveform(xdata)
        super().receiveYWaveform(ydata)
