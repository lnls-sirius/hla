#!/usr/bin/env python3.6
from pydm.PyQt.uic import loadUi
from pydm.PyQt.QtGui import QMainWindow, QApplication
from pydm import PyDMApplication
import sys
import socket


class LTBPosAngCorr(QMainWindow):
    def __init__(self, parent=None):
        super(LTBPosAngCorr, self).__init__(parent)
        self.centralwidget = loadUi('/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla/tb_ap_posang/ui_tb_ap_posang.ui')
        self.setCentralWidget(self.centralwidget)

        widget2pv_list = [[self.centralwidget.PyDMLineEdit_OrbXDeltaPos_SP, 'TB-Glob:AP-PosAng:DeltaPosX-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbXDeltaPos_SP,'TB-Glob:AP-PosAng:DeltaPosX-SP'],
                          [self.centralwidget.PyDMLabel_OrbXDeltaPos_RB,    'TB-Glob:AP-PosAng:DeltaPosX-RB'],
                          [self.centralwidget.PyDMLineEdit_OrbXDeltaAng_SP, 'TB-Glob:AP-PosAng:DeltaAngX-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbXDeltaAng_SP,'TB-Glob:AP-PosAng:DeltaAngX-SP'],
                          [self.centralwidget.PyDMLabel_OrbXDeltaAng_RB,    'TB-Glob:AP-PosAng:DeltaAngX-RB'],
                          [self.centralwidget.PyDMLineEdit_OrbYDeltaPos_SP, 'TB-Glob:AP-PosAng:DeltaPosY-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbYDeltaPos_SP,'TB-Glob:AP-PosAng:DeltaPosY-SP'],
                          [self.centralwidget.PyDMLabel_OrbYDeltaPos_RB,    'TB-Glob:AP-PosAng:DeltaPosY-RB'],
                          [self.centralwidget.PyDMLineEdit_OrbYDeltaAng_SP, 'TB-Glob:AP-PosAng:DeltaAngY-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbYDeltaAng_SP,'TB-Glob:AP-PosAng:DeltaAngY-SP'],
                          [self.centralwidget.PyDMLabel_OrbYDeltaAng_RB,    'TB-Glob:AP-PosAng:DeltaAngY-RB'],
                          [self.centralwidget.PyDMPushButton_SetNewRef,     'TB-Glob:AP-PosAng:SetNewRef-Cmd']]
        self.set_widgets_channel(widget2pv_list)

        # Estabilish widget connections
        self.app = QApplication.instance()
        self.app.establish_widget_connections(self)

    def set_widgets_channel(self,widget2pv_list):
        """Receive lists:
        widget_list --list of widgets to set channel
        pv_list     --list of correspondent pvs
        And sets the PyDMWidgets channels"""
        for widget,pv in widget2pv_list:
            wname = widget.objectName().split('_')
            if wname[0] in ('PyDMLineEdit','PyDMScrollBar'):
                widget.channel = 'ca://' + 'fac-' + socket.gethostname() + '-' + pv
            elif wname[0] in ('PyDMLabel'):
                widget.setChannel('ca://' + 'fac-' + socket.gethostname() + '-' + pv)

    def closeEvent(self, event):
        """Reimplement close event to close widget connections."""
        self.app.close_widget_connections(self)
        super().closeEvent(event)

if __name__ == '__main__':
    app = PyDMApplication(None, sys.argv)
    window = LTBPosAngCorr()
    window.show()
    sys.exit(app.exec_())
