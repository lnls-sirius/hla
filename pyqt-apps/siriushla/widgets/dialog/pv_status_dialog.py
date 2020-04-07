"""Status PV detail dialog."""

import time as _time

from qtpy.QtWidgets import QGridLayout, QLabel

from siriuspy.namesys import SiriusPVName
from siriushla.widgets.windows import SiriusDialog
from siriushla.widgets.signal_channel import SiriusConnectionSignal
from siriushla.widgets.led import SiriusLedAlert


class StatusDetailDialog(SiriusDialog):
    """Status Detail Dialog."""

    def __init__(self, pvname='', labels=list(), parent=None):
        super().__init__(parent)
        self.pvname = SiriusPVName(pvname)
        self.section = self.pvname.sec
        self.setObjectName(self.section+'App')
        self.labels = labels
        if not labels:
            labels_pv = pvname.replace('-Mon', 'Labels-Cte')
            ch = SiriusConnectionSignal(labels_pv)
            for i in range(20):
                if ch.connected:
                    break
                _time.sleep(0.1)
            if not ch.connected:
                raise ConnectionError(labels_pv + ' not connected!')
            self.labels = ch.value.split('\n')
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        for idx, desc in enumerate(self.labels):
            led = SiriusLedAlert(self, self.pvname, bit=idx)
            lbl = QLabel(desc, self)
            lay.addWidget(led, idx, 0)
            lay.addWidget(lbl, idx, 1)
