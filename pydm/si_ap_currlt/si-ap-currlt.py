from pydm import Display
from pydm.PyQt.QtCore import pyqtSlot
from epics import PV
from os import path

class showCurrLT(Display):
    def __init__(self, parent=None, args=None):
        super(showCurrLT, self).__init__(parent=parent)
        self.ui.PyDMMultiTimePlot.trace0_receive_value.connect(self.formatCurrLT)
        self.ui.CurrLT.setText("0:00:00")

    def ui_filename(self):
        return 'si-ap-currlt.ui'

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

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
        self.ui.CurrLT.setText(lt_str)

intelclass = showCurrLT
