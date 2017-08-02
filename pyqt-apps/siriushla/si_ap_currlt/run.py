#!/usr/bin/env python3.6
import sys
from pydm import PyDMApplication
from pydm.PyQt.uic import loadUi
from pydm.PyQt.QtCore import pyqtSlot
from pydm.PyQt.QtGui import QMainWindow
from os import path

class CurrLTWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CurrLTWindow, self).__init__(parent)
        self.centralwidget = loadUi('si-ap-currlt.ui')
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.PyDMMultiTimePlot.trace0_receive_value.connect(self.formatCurrLT)
        self.centralwidget.CurrLT.setText("0:00:00")

    @pyqtSlot(float)
    def formatCurrLT(self, value):
        lt = value
        H = str(int(lt//3600))
        m = str(int((lt%3600)//60))
        if len(m)==1:
            m = '0' + m
        s = str(int((lt%3600)%60))
        if len(s)==1:
            s = '0' + s
        lt_str = H +':'+ m +':'+ s
        self.centralwidget.CurrLT.setText(lt_str)

app = PyDMApplication(None, sys.argv)
window = CurrLTWindow()
window.show()
sys.exit(app.exec_())
