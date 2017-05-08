import sys, re
from pydm.PyQt.QtCore import *
from pydm.PyQt.QtGui import *
from siriuspy.namesys import SiriusPVName
from CyclePowerSupplies import CyclePowerSupplies


class CommandThread(QThread):
    def __init__(self, obj, method=None, parent=None):
        super(CommandThread, self).__init__(parent)
        self.obj = obj
        self.method = method

    def run(self):
        getattr(self.obj, self.method)()
