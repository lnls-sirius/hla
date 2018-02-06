#!/usr/bin/env python-sirius
"""HLA Current and Lifetime Modules."""

import epics as _epics
import numpy as _np
from pydm.PyQt.uic import loadUi
from pydm.PyQt.QtCore import pyqtSlot
from siriushla.widgets import SiriusMainWindow
from pydm.utilities.macro import substitute_in_file as _substitute_in_file


class CurrLTWindow(SiriusMainWindow):
    """Class to include some intelligence in the .ui file."""

    def __init__(self, parent=None, prefix=None, acc=None):
        """Initialize some widgets."""
        super(CurrLTWindow, self).__init__(parent)
        UI_FILE = ('/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla/'
                   'as_ap_currlt/ui_'+acc.lower()+'_ap_currlt.ui')
        tmp_file = _substitute_in_file(UI_FILE, {'PREFIX': prefix})

        self.centralwidget = loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle(acc.upper()+' Current Info: Current and Lifetime')

        self.lifetime_pv = _epics.PV(
            prefix+acc.upper()+'-Glob:AP-CurrInfo:Lifetime-Mon')
        self.lifetime_pv.add_callback(self.formatLifetime)
        self.centralwidget.CurrLT.setText("0:00:00")

        self.centralwidget.spinBox.valueChanged.connect(
            self.setGraphBufferSize)
        self.centralwidget.spinBox_2.valueChanged.connect(
            self.setGraphTimeSpan)
        self.centralwidget.checkBox.stateChanged.connect(
            self.setCurrentTraceVisibility)
        self.centralwidget.checkBox_2.stateChanged.connect(
            self.setLifetimeTraceVisibility)

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

    @pyqtSlot(int)
    def setGraphBufferSize(self, value):
        """Set graph buffer size."""
        self.centralwidget.PyDMTimePlot.setBufferSize(value)

    @pyqtSlot(int)
    def setGraphTimeSpan(self, value):
        """Set graph time span."""
        self.centralwidget.PyDMTimePlot.setTimeSpan(float(value))

    @pyqtSlot(int)
    def setCurrentTraceVisibility(self, value):
        """Set current trace visibility."""
        self.centralwidget.PyDMTimePlot._curves[0].setVisible(value)

    @pyqtSlot(int)
    def setLifetimeTraceVisibility(self, value):
        """Set lifetime trace visibility."""
        self.centralwidget.PyDMTimePlot._curves[1].setVisible(value)
