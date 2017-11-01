#!/usr/bin/env python-sirius

"""HLA as_ap_posang module."""

from pydm.PyQt.uic import loadUi as _loadUi
from pydm.PyQt.QtGui import QMainWindow as _QMainWindow
from pydm.PyQt.QtGui import QApplication as _QApplication
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy.envars import vaca_prefix as _vaca_prefix

UI_FILE = ('/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla/'
           'as_ap_posang/ui_as_ap_posang.ui')


class ASAPPosAngCorr(_QMainWindow):
    """Main Class."""

    def __init__(self, parent=None, prefix=None, tl=None):
        """Init method."""
        super(ASAPPosAngCorr, self).__init__(parent)

        tmp_file = _substitute_in_file(UI_FILE, {'TRANSPORTLINE': tl.upper()})
        self.centralwidget = _loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)

        self._prefix = prefix
        widget2pv_list = [[self.centralwidget.PyDMLineEdit_OrbXDeltaPos_SP,
                           tl.upper() + '-Glob:AP-PosAng:DeltaPosX-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbXDeltaPos_SP,
                           tl.upper() + '-Glob:AP-PosAng:DeltaPosX-SP'],
                          [self.centralwidget.PyDMLabel_OrbXDeltaPos_RB,
                           tl.upper() + '-Glob:AP-PosAng:DeltaPosX-RB'],
                          [self.centralwidget.PyDMLineEdit_OrbXDeltaAng_SP,
                           tl.upper() + '-Glob:AP-PosAng:DeltaAngX-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbXDeltaAng_SP,
                           tl.upper() + '-Glob:AP-PosAng:DeltaAngX-SP'],
                          [self.centralwidget.PyDMLabel_OrbXDeltaAng_RB,
                           tl.upper() + '-Glob:AP-PosAng:DeltaAngX-RB'],
                          [self.centralwidget.PyDMLineEdit_OrbYDeltaPos_SP,
                           tl.upper() + '-Glob:AP-PosAng:DeltaPosY-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbYDeltaPos_SP,
                           tl.upper() + '-Glob:AP-PosAng:DeltaPosY-SP'],
                          [self.centralwidget.PyDMLabel_OrbYDeltaPos_RB,
                           tl.upper() + '-Glob:AP-PosAng:DeltaPosY-RB'],
                          [self.centralwidget.PyDMLineEdit_OrbYDeltaAng_SP,
                           tl.upper() + '-Glob:AP-PosAng:DeltaAngY-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbYDeltaAng_SP,
                           tl.upper() + '-Glob:AP-PosAng:DeltaAngY-SP'],
                          [self.centralwidget.PyDMLabel_OrbYDeltaAng_RB,
                           tl.upper() + '-Glob:AP-PosAng:DeltaAngY-RB'],
                          [self.centralwidget.PyDMPushButton_SetNewRef,
                           tl.upper() + '-Glob:AP-PosAng:SetNewRef-Cmd']]
        self.set_widgets_channel(widget2pv_list, prefix)

        # Estabilish widget connections
        self.app = _QApplication.instance()
        self.app.establish_widget_connections(self)

    def set_widgets_channel(self, widget2pv_list, prefix):
        """Receive lists and prefix.

        widget_list --list of widgets to set channel
        pv_list     --list of correspondent pvs
        And sets the PyDMWidgets channels
        """
        if prefix is None:
            prefix = _vaca_prefix
        for widget, pv in widget2pv_list:
            widget.channel = 'ca://' + prefix + pv

    def closeEvent(self, event):
        """Reimplement close event to close widget connections."""
        self.app.close_widget_connections(self)
        super().closeEvent(event)
