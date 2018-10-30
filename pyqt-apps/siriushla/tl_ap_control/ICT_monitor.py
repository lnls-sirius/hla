#!/usr/bin/env python-sirius
"""HLA TB and TS ICT monitoring Window."""

import sys
from qtpy.uic import loadUi
from qtpy.QtCore import Slot
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow
from siriushla import util


class ICTMonitoring(SiriusMainWindow):
    """Class to create ICTs History Monitor Window."""

    def __init__(self, tl, parent=None, prefix=None):
        """Create graphs."""
        super(ICTMonitoring, self).__init__(parent)
        tmp_file = _substitute_in_file(
            '/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla'
            '/tl_ap_control/ui_tl_ap_ictmon.ui', {'TL': tl.upper()})
        self.centralwidget = loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)
        if tl.upper() == 'TB':
            ICT1_channel = prefix + 'TB-02:DI-ICT'
            ICT2_channel = prefix + 'TB-04:DI-ICT'
        elif tl.upper() == 'TS':
            ICT1_channel = prefix + 'TS-01:DI-ICT'
            ICT2_channel = prefix + 'TS-04:DI-ICT'
        self.centralwidget.PyDMTimePlot_Charge.addYChannel(
            y_channel=ICT1_channel + ':Charge-Mon',
            name='Charge ICT1', color='red', lineWidth=2)
        self.centralwidget.PyDMTimePlot_Charge.addYChannel(
            y_channel=ICT2_channel + ':Charge-Mon',
            name='Charge ICT2', color='blue', lineWidth=2)
        self.centralwidget.PyDMWaveformPlot_ChargeHstr.addChannel(
            y_channel=ICT1_channel + ':ChargeHstr-Mon',
            name='Charge History ICT1', color='red', lineWidth=2)
        self.centralwidget.PyDMWaveformPlot_ChargeHstr.addChannel(
            y_channel=ICT2_channel + ':ChargeHstr-Mon',
            name='Charge History ICT2', color='blue', lineWidth=2)

        self.centralwidget.checkBox.stateChanged.connect(
            self._setICT1CurveVisibility)
        self.centralwidget.checkBox_2.stateChanged.connect(
            self._setICT2CurveVisibility)

    @Slot(int)
    def _setICT1CurveVisibility(self, value):
        """Set curves visibility."""
        self.centralwidget.PyDMTimePlot_Charge._curves[0].setVisible(value)
        self.centralwidget.PyDMWaveformPlot_ChargeHstr._curves[0].setVisible(
            value)

    @Slot(int)
    def _setICT2CurveVisibility(self, value):
        """Set curves visibility."""
        self.centralwidget.PyDMTimePlot_Charge._curves[1].setVisible(value)
        self.centralwidget.PyDMWaveformPlot_ChargeHstr._curves[1].setVisible(
            value)


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    util.set_style(app)
    w = ICTMonitoring(tl='TB', prefix=_vaca_prefix)
    w.show()
    sys.exit(app.exec_())
