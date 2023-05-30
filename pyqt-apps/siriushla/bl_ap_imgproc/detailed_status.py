from epics import caget

from qtpy.QtWidgets import QWidget, QLabel, QGridLayout
from siriushla.widgets.led import SiriusLedAlert

from ..widgets.windows import SiriusMainWindow

from .util import DVF_STATUS


class DetailedStatusWindow(SiriusMainWindow):

    def __init__(self, device, parent=None):
        """."""
        super().__init__(parent=parent)
        self.device = device
        self.pvname = self.device + ':' + DVF_STATUS[0]
        self.setWindowTitle("DVF Status Detailed")
        self.setObjectName("SIApp")
        self.setupUi()

    def detailed_labels(self):
        pvname = self.device + ':' + DVF_STATUS[1]
        labels = caget(pvname)

        label_list = []
        try:
            for label in labels.tolist():
                label_list.append(label)
        except:
            raise ConnectionError(pvname + ' not connected!')

        return label_list

    def setupUi(self):
        wid = QWidget()
        self.labels = self.detailed_labels()
        lay = QGridLayout(self)
        for idx, desc in enumerate(self.labels):
            led = SiriusLedAlert(self, self.pvname, bit=idx)
            lbl = QLabel(desc, self)
            lay.addWidget(led, idx+1, 0)
            lay.addWidget(lbl, idx+1, 1)
        wid.setLayout(lay)

        self.setCentralWidget(wid)
