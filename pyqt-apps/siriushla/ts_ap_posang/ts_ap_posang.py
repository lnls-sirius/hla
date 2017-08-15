#!/usr/bin/env python-sirius

"""HLA as_ap_posang module."""

import sys as _sys
from pydm.PyQt.uic import loadUi as _loadUi
from pydm.PyQt.QtGui import QMainWindow as _QMainWindow
from pydm.PyQt.QtGui import QApplication as _QApplication
from siriuspy import envars as _envars
from pydm import PyDMApplication as _PyDMApplication


class BTSPosAngCorr(_QMainWindow):
    """Main Class."""

    def __init__(self, parent=None):
        """Init method."""
        super(BTSPosAngCorr, self).__init__(parent)
        self.centralwidget = _loadUi(
            '/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla/' +
            'ts_ap_posang/ui_ts_ap_posang.ui')
        self.setCentralWidget(self.centralwidget)

        widget2pv_list = [
            [self.centralwidget.PyDMLineEdit_OrbXDeltaPos_SP,
                'TS-Glob:AP-PosAng:DeltaPosX-SP'],
            [self.centralwidget.PyDMScrollBar_OrbXDeltaPos_SP,
                'TS-Glob:AP-PosAng:DeltaPosX-SP'],
            [self.centralwidget.PyDMLabel_OrbXDeltaPos_RB,
                'TS-Glob:AP-PosAng:DeltaPosX-RB'],
            [self.centralwidget.PyDMLineEdit_OrbXDeltaAng_SP,
                'TS-Glob:AP-PosAng:DeltaAngX-SP'],
            [self.centralwidget.PyDMScrollBar_OrbXDeltaAng_SP,
                'TS-Glob:AP-PosAng:DeltaAngX-SP'],
            [self.centralwidget.PyDMLabel_OrbXDeltaAng_RB,
                'TS-Glob:AP-PosAng:DeltaAngX-RB'],
            [self.centralwidget.PyDMLineEdit_OrbYDeltaPos_SP,
                'TS-Glob:AP-PosAng:DeltaPosY-SP'],
            [self.centralwidget.PyDMScrollBar_OrbYDeltaPos_SP,
                'TS-Glob:AP-PosAng:DeltaPosY-SP'],
            [self.centralwidget.PyDMLabel_OrbYDeltaPos_RB,
                'TS-Glob:AP-PosAng:DeltaPosY-RB'],
            [self.centralwidget.PyDMLineEdit_OrbYDeltaAng_SP,
                'TS-Glob:AP-PosAng:DeltaAngY-SP'],
            [self.centralwidget.PyDMScrollBar_OrbYDeltaAng_SP,
                'TS-Glob:AP-PosAng:DeltaAngY-SP'],
            [self.centralwidget.PyDMLabel_OrbYDeltaAng_RB,
                'TS-Glob:AP-PosAng:DeltaAngY-RB'],
            [self.centralwidget.PyDMPushButton_SetNewRef,
                'TS-Glob:AP-PosAng:SetNewRef-Cmd']]
        self.set_widgets_channel(widget2pv_list)

        # Estabilish widget connections
        self.app = _QApplication.instance()
        self.app.establish_widget_connections(self)

    def set_widgets_channel(self, widget2pv_list):
        """Receive lists."""
        """widget_list --list of widgets to set channel
        pv_list     --list of correspondent pvs
        And sets the PyDMWidgets channels"""
        for widget, pv in widget2pv_list:
            wname = widget.objectName().split('_')
            if wname[0] in ('PyDMLineEdit', 'PyDMScrollBar'):
                widget.channel = 'ca://' + _envars.vaca_prefix + pv
            elif wname[0] in ('PyDMLabel'):
                widget.setChannel('ca://' + _envars.vaca_prefix + pv)

    def closeEvent(self, event):
        """Reimplement close event to close widget connections."""
        self.app.close_widget_connections(self)
        super().closeEvent(event)


if __name__ == '__main__':
    app = _PyDMApplication(None, _sys.argv)
    window = BTSPosAngCorr()
    window.show()
    _sys.exit(app.exec_())
