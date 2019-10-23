#!/usr/bin/env python-sirius
"""HLA Current and Lifetime Modules."""

import os as _os
import epics as _epics
import numpy as _np
from qtpy.uic import loadUi
from qtpy.QtCore import Slot
from siriushla.widgets import SiriusMainWindow
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy.envars import vaca_prefix as _vaca_prefix


class CurrLTWindow(SiriusMainWindow):
    """Class to include some intelligence in the .ui file."""

    def __init__(self, parent=None, prefix=_vaca_prefix):
        """Initialize some widgets."""
        super(CurrLTWindow, self).__init__(parent)

        UI_FILE = (_os.path.abspath(_os.path.dirname(__file__)) +
                   '/ui_si_ap_currlt.ui')
        tmp_file = _substitute_in_file(UI_FILE, {'PREFIX': prefix})

        self.centralwidget = loadUi(tmp_file)
        self.setObjectName('SIApp')
        self.centralwidget.setObjectName('SIApp')
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle('SI Current Info: Current and Lifetime')

        self.lifetime_pv = _epics.PV(
            prefix+'SI-Glob:AP-CurrInfo:Lifetime-Mon')
        self.lifetime_pv.add_callback(self.formatLifetime)
        self.centralwidget.CurrLT.setText("0:00:00")

        self.centralwidget.spinBox.valueChanged.connect(
            self.setGraphBufferSize)
        self.centralwidget.spinBox_2.valueChanged.connect(
            self.setGraphTimeSpan)

    def formatLifetime(self, value, **kws):
        """Format lifetime label."""
        lt = value
        if not _np.isnan(lt):
            H = str(int(lt // 3600))
            m = str(int((lt % 3600) // 60))
            if len(m) == 1:
                m = '0' + m
            s = str(int((lt % 3600) % 60))
            if len(s) == 1:
                s = '0' + s
            lt_str = H + ':' + m + ':' + s
            self.centralwidget.CurrLT.setText(lt_str)

    @Slot(int)
    def setGraphBufferSize(self, value):
        """Set graph buffer size."""
        self.centralwidget.PyDMTimePlot_Current.setBufferSize(value)
        self.centralwidget.PyDMTimePlot_Lifetime.setBufferSize(value)

    @Slot(int)
    def setGraphTimeSpan(self, value):
        """Set graph time span."""
        self.centralwidget.PyDMTimePlot_Current.setTimeSpan(float(value))
        self.centralwidget.PyDMTimePlot_Lifetime.setTimeSpan(float(value))
