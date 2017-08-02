"""Create the Selection Matrices for BPMs and Correctors."""

import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QSizePolicy, QSpacerItem)
from pydm import PyDMApplication
from pydm.widgets.checkbox import PyDMCheckbox
from pydm.widgets.led import PyDMLed

SOFB_PREFIX = 'ca://SI-Glob:AP-SOFB:'
NR_BPMs = 160
NR_CHs = 120
NR_CVs = 160


class SelectionMatrix(QVBoxLayout):
    """Create the Selection Matrices for BPMs and Correctors."""

    SUBSECTIONS = {
        'BPMX': ('M1', 'M2', 'C1-1', 'C1-2', 'C2', 'C3-1', 'C3-2', 'C4'),
        'BPMY': ('M1', 'M2', 'C1-1', 'C1-2', 'C2', 'C3-1', 'C3-2', 'C4'),
        'CV':   ('M1', 'M2', 'C1', 'C2-1', 'C2-2', 'C3-1', 'C3-2', 'C4'),
        'CH':   ('M1', 'M2', 'C1', 'C2', 'C3', 'C4')}
    INDICES_LENGTH = {
        'BPMX': NR_BPMs, 'BPMY': NR_BPMs, 'CH': NR_CHs, 'CV': NR_CVs}

    def __init__(self, parent, dev):
        """Initialize the matrix of the specified dev."""
        super().__init__(parent)
        self.dev = dev
        self._setupUi()

    def _setupUi(self):
        subsecs, indices = self._get_matrix_params()
        secs = ['{0:02d}'.format(i) for i in range(1, 21)]
        len_ = len(subsecs)
        wid2 = self._make_line('00', subsecs, list(range(len_)), True)
        self.addWidget(wid2)
        for i, sec in enumerate(secs):
            wid2 = self._make_line(sec, subsecs,
                                   indices[i*len_:(i+1)*len_], False)
            self.addWidget(wid2)

    def _get_matrix_params(self):
        indices = list(range(self.INDICES_LENGTH[self.dev]-1))
        indices = [self.INDICES_LENGTH[self.dev]-1] + indices
        return self.SUBSECTIONS[self.dev], indices

    def _make_line(self, section, subsections, indices, header):
        label = section+self.dev
        wid = QWidget()
        if int(section) % 2:
            wid.setStyleSheet('background-color: rgb(220, 220, 220);')
        wid.setObjectName('Wid_'+label)
        hl = QHBoxLayout(wid)
        hl.setObjectName('HL_'+label)
        hspace = QSpacerItem(40, 20,
                             QSizePolicy.Expanding, QSizePolicy.Minimum)
        hl.addItem(hspace)
        lab = QLabel(wid)
        lab.setObjectName('LB_'+label)
        lab.setText('  ' if header else section)
        hl.addWidget(lab)
        hspace = QSpacerItem(40, 20,
                             QSizePolicy.Expanding, QSizePolicy.Minimum)
        hl.addItem(hspace)
        for subsection, index in zip(subsections, indices):
            if header:
                lab = QLabel(wid)
                lab.setObjectName('LB_' + self.dev+subsection)
                lab.setText(subsection)
                hl.addWidget(lab)
            else:
                subhl = self._make_unit(wid, section, subsection, index)
                hl.addLayout(subhl)
            hspace = QSpacerItem(40, 20,
                                 QSizePolicy.Expanding, QSizePolicy.Minimum)
            hl.addItem(hspace)
        return wid

    def _make_unit(self, parent, section, subsection, index):
        label = self.dev+section+subsection
        hl = QHBoxLayout()
        hl.setObjectName('HL_'+label)
        cb = PyDMCheckbox(parent)
        cb.setObjectName('PyDMCB_'+label)
        cb.setToolTip(label)
        cb.channel = SOFB_PREFIX+self.dev+'EnblList-SP'
        cb.pvbit = index
        hl.addWidget(cb)
        led = PyDMLed(parent)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        led.setSizePolicy(sizePolicy)
        led.setObjectName('PyDMLed_'+label)
        led.setToolTip(label)
        led.channel = SOFB_PREFIX+self.dev+'EnblList-RB'
        led.pvbit = index
        hl.addWidget(led)
        return hl


#    QtCore.QMetaObject.connectSlotsByName(Form)
if __name__ == '__main__':
    app = PyDMApplication()
    widget = QWidget()
    SelectionMatrix(widget, 'BPMX')
    widget.show()
    sys.exit(app.exec_())
