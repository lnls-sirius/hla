"""Status PV detail dialog."""

import time as _time

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel

from siriuspy.namesys import SiriusPVName
from siriushla.widgets.windows import SiriusDialog
from siriushla.widgets.signal_channel import SiriusConnectionSignal
from siriushla.widgets.led import SiriusLedAlert


class StatusDetailDialog(SiriusDialog):
    """Status Detail Dialog."""

    def __init__(
            self, pvname='', labels=None, pvname_labels='',
            section='', parent=None, title=''):
        super().__init__(parent)
        try:
            self.pvname = SiriusPVName(pvname)
        except:
            self.pvname = pvname
        self.section = section
        if not section:
            self.section = self.pvname.sec
        self.setObjectName(self.section+'App')
        self.labels = list() if labels is None else labels
        self.title = title
        if not labels:
            labels_pv = pvname_labels or pvname.replace('-Mon', 'Labels-Cte')
            ch = SiriusConnectionSignal(labels_pv)
            ch.new_value_signal[str].connect(self._updateLabels)
            ch.new_value_signal[list].connect(self._updateLabels)
        self._setupUi()

    def _setupUi(self):
        if self.title:
            label = QLabel('<h4>'+self.title+'</h4>',
                           self, alignment=Qt.AlignCenter)
        else:
            label = QLabel('<h4>'+self.pvname.device_name+'</h4>',
                           self, alignment=Qt.AlignCenter)
        lay = QGridLayout(self)
        lay.addWidget(label, 0, 0, 1, 2)
        self._fillLabels()

    def _updateLabels(self, labels):
        if isinstance(labels, str):
            labels = labels.split('\n')
        self.labels = labels
        self._fillLabels()

    def _fillLabels(self):
        for idx, desc in enumerate(self.labels):
            led = SiriusLedAlert(self, self.pvname, bit=idx)
            lbl = QLabel(desc, self)
            self.layout().addWidget(led, idx+1, 0)
            self.layout().addWidget(lbl, idx+1, 1)
