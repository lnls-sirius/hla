"""Custom widgets."""

import numpy as np
from pydm.widgets import PyDMLineEdit
from pydm.widgets.waveformplot import WaveformCurveItem
from qtpy.QtCore import Slot
from siriuspy.search import IDSearch

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

    def __init__(self, idname, section, **kwargs):
        """Sectioned waveform curve item."""
        super().__init__(**kwargs)
        self.section = section

        # NOTE: Up to now FF tables in beaglebones
        # interpolate from zero to maximum gap (kparam),
        # instead of using the actual gap values.
        param = IDSearch.conv_idname_2_parameters(idname)
        self.kparam_min = 0  # [mm]
        self.kparam_max = param.KPARAM_MAX

    @Slot(np.ndarray)
    def receiveYWaveform(self, new_waveform):
        size = len(new_waveform) / 4
        mini = int(size * self.section)
        maxi = int(size * (self.section + 1))
        ydata = new_waveform[mini:maxi]
        npts = len(ydata)
        kmin, kmax = self.kparam_min, self.kparam_max
        grid = np.arange(0, npts) / (npts - 1)
        xdata = kmin + (kmax - kmin) * grid
        super().receiveXWaveform(xdata)
        super().receiveYWaveform(ydata)
