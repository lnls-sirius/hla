import sys, re
from pydm.PyQt.QtCore import *
from pydm.PyQt.QtGui import *
from siriuspy.namesys import SiriusPVName
from CyclePowerSupplies import CyclePowerSupplies


class CyclingThread(QThread):
    def __init__(self, cycle_obj, parent=None):
        super(CyclingThread, self).__init__(parent)
        self.cycle_obj = cycle_obj

    def run(self):
        self.cycle_obj.setToCycle()
        self.cycle_obj.printBadPS()
