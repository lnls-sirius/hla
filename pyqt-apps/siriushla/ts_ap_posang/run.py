#!/usr/bin/env python3.6
from pydm.PyQt.uic import loadUi
from pydm import PyDMApplication
import sys

# class BTSPosAngCorr(QMainWindow):
#     def __init__(self, parent=None):
#         super(BTSPosAngCorr, self).__init__(parent)
#         self.centralwidget = loadUi('ts_ap_posang.ui')
#         self.setCentralWidget(self.centralwidget)

app = PyDMApplication(None, sys.argv)
window = loadUi('ts_ap_posang.ui')
window.show()
sys.exit(app.exec_())
