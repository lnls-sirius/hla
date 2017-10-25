"""Create the Selection Matrices for BPMs and Correctors."""

import sys
import numpy as np
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QSizePolicy, QSpacerItem, QCheckBox)
from pydm import PyDMApplication
from pydm.widgets.base import PyDMWidget, PyDMWritableWidget
from siriushla.widgets.led import PyDMLed
from siriushla.widgets.QLed import QLed

NR_BPMs = 160
NR_CHs = 120
NR_CVs = 160


class _PyDMCheckBoxList(PyDMWritableWidget, QWidget):

    def __init__(self, parent=None, init_channel=None, size=0):
        QWidget.__init__(self, parent=parent)
        PyDMWritableWidget.__init__(self, init_channel=init_channel)
        self.setVisible(False)
        self.cb_list = []
        for i in range(size):
            cb = QCheckBox()
            cb.clicked.connect(self._send_value_index(i))
            self.cb_list.append(cb)

    def _send_value_index(self, index):
        def send_value(checked):
            if self.value is None:
                return
            self.value[index] = checked
            self.send_value_signal[np.ndarray].emit(self.value)
        return send_value

    def value_changed(self, new_val):
        super(_PyDMCheckBoxList, self).value_changed(new_val)
        for i, checked in enumerate(self.value):
            self.cb_list[i].setChecked(checked)


class _PyDMLedList(PyDMWidget, QWidget):

    def __init__(self, parent=None, init_channel=None, size=0):
        QWidget.__init__(self, parent=parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.setVisible(False)
        self.led_list = []
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for i in range(size):
            led = QLed()
            led.setOffColor(PyDMLed.default_colorlist[0])
            led.setOnColor(PyDMLed.default_colorlist[1])
            led.setSizePolicy(sizePolicy)
            self.led_list.append(led)

    def value_changed(self, new_val):
        super(_PyDMLedList, self).value_changed(new_val)
        for i, checked in enumerate(self.value):
            self.led_list[i].setState(checked)


class SelectionMatrix(QVBoxLayout):
    """Create the Selection Matrices for BPMs and Correctors."""

    SUBSECTIONS = {
        'BPMX': ('M1', 'M2', 'C1-1', 'C1-2', 'C2', 'C3-1', 'C3-2', 'C4'),
        'BPMY': ('M1', 'M2', 'C1-1', 'C1-2', 'C2', 'C3-1', 'C3-2', 'C4'),
        'CV':   ('M1', 'M2', 'C1', 'C2-1', 'C2-2', 'C3-1', 'C3-2', 'C4'),
        'CH':   ('M1', 'M2', 'C1', 'C2', 'C3', 'C4')}
    INDICES_LENGTH = {
        'BPMX': NR_BPMs, 'BPMY': NR_BPMs, 'CH': NR_CHs, 'CV': NR_CVs}

    def __init__(self, parent, dev, prefix):
        """Initialize the matrix of the specified dev."""
        super().__init__(parent)
        self.prefix = prefix
        self.dev = dev
        self.PV_sp = _PyDMCheckBoxList(
                parent=None,
                init_channel=self.prefix + self.dev + 'EnblList-SP',
                size=self.INDICES_LENGTH[self.dev])
        self.PV_rb = _PyDMLedList(
                parent=None,
                init_channel=self.prefix + self.dev + 'EnblList-RB',
                size=self.INDICES_LENGTH[self.dev])
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
        cb = self.PV_sp.cb_list[index]
        cb.setParent(parent)
        cb.setToolTip(label)
        hl.addWidget(cb)

        led = self.PV_rb.led_list[index]
        led.setParent(parent)
        led.setToolTip(label)
        hl.addWidget(led)
        return hl


if __name__ == '__main__':
    app = PyDMApplication()
    widget = QWidget()
    SelectionMatrix(widget, 'BPMX')
    widget.show()
    sys.exit(app.exec_())
