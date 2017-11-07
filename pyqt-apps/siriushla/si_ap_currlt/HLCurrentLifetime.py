#!/usr/bin/env python-sirius
"""HLA Current and Lifetime Modules."""

from pydm.PyQt.uic import loadUi
from pydm.PyQt.QtCore import pyqtSlot
from siriushla.widgets import SiriusMainWindow
from pydm.utilities.macro import substitute_in_file as _substitute_in_file

UI_FILE = ('/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla/'
           'si_ap_currlt/ui_si_ap_currlt.ui')


class CurrLTWindow(SiriusMainWindow):
    """Class to include some intelligence in the .ui file."""

    def __init__(self, parent=None, prefix=None):
        """Initialize some widgets."""
        super(CurrLTWindow, self).__init__(parent)
        tmp_file = _substitute_in_file(UI_FILE, {'PREFIX': prefix})
        self.centralwidget = loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.PyDMMultiTimePlot.trace1_receive_value.connect(
            self.formatLifetime)
        self.centralwidget.CurrLT.setText("0:00:00")

    @pyqtSlot(float)
    def formatLifetime(self, value):
        """Format lifetime label."""
        lt = value
        H = str(int(lt // 3600))
        m = str(int((lt % 3600) // 60))
        if len(m) == 1:
            m = '0' + m
        s = str(int((lt % 3600) % 60))
        if len(s) == 1:
            s = '0' + s
        lt_str = H + ':' + m + ':' + s
        self.centralwidget.CurrLT.setText(lt_str)
