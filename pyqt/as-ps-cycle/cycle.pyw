#!/usr/local/bin/python3.6

import sys
from pydm.PyQt.QtCore import *
#from pydm.PyQt.QtWidgets import *
from pydm.PyQt.QtGui import *
from pydm import PyDMApplication
from CyclePowerSupplies import CyclePowerSupplies
from PsCycleMenuWidget import PsCycleMenuWidget
from PsCycleStatusWidget import PsCycleStatusWidget
from CyclingThread import CyclingThread


class PsCycleWindow(QDialog):
    def __init__(self, parent=None):
        super(PsCycleWindow, self).__init__(parent)

        self.setWindowTitle("Power Supply Cycling")

        cycleMenuWidget = PsCycleMenuWidget(self)
        menuLayout = QVBoxLayout()
        menuLayout.addWidget(cycleMenuWidget)
        menuLayout.addStretch()
        statusWidget = PsCycleStatusWidget(self)

        grid = QGridLayout()
        grid.addLayout(menuLayout, 0, 0)
        grid.addWidget(statusWidget, 0, 1)
        self.setLayout(grid)
        self.setMinimumHeight(600)



if __name__ == '__main__':
    app = PyDMApplication(None, sys.argv)
    window = PsCycleWindow()
    window.show()
    app.exec_()
