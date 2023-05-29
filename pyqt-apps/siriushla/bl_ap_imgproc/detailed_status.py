from epics import caget

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QWidget, \
    QVBoxLayout, QLabel
from qtpy.QtGui import QColor
from pydm.widgets import PyDMByteIndicator

from ..widgets.windows import SiriusMainWindow

from .util import DVF_STATUS


class DetailedStatusWindow(SiriusMainWindow):

    def __init__(self, device, parent=None):
        """."""
        super().__init__(parent=parent)
        self.device = device
        self.setWindowTitle("DVF Status Detailed")
        self.setObjectName("SIApp")

        self.setupUi()

    def bit_indicator(self):
        pvname = self.device + ':' + DVF_STATUS[0]
        bit_wid = PyDMByteIndicator(init_channel=pvname)
        bit_wid.numBits = 8
        bit_wid.onColor = QColor(0, 190, 0)
        bit_wid.offColor = QColor(20, 80, 10)
        return bit_wid

    def detailed_labels(self):
        pvname = self.device + ':' + DVF_STATUS[1]
        labels = caget(pvname)

        count = 0
        vlay = QVBoxLayout()
        label_list = labels.tolist()
        for label in label_list:
            txt_wid = QLabel(label)
            txt_wid.setAlignment(Qt.AlignVCenter)
            vlay.addWidget(txt_wid)
            count += 1

        for label in range(count, 8):
            txt_wid = QLabel("")
            vlay.addWidget(txt_wid)
        return vlay

    def setupUi(self):
        wid = QWidget()
        hlay = QHBoxLayout()
        wid.setLayout(hlay)

        bit_ind = self.bit_indicator()
        hlay.addWidget(bit_ind)

        labels = self.detailed_labels()
        hlay.addLayout(labels)

        self.setCentralWidget(wid)
