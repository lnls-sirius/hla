"""Create the Selection Matrices for BPMs and Correctors."""

from functools import partial as _part
import numpy as np
from PyQt5.QtWidgets import (
    QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QSpacerItem,
    QScrollArea, QWidget, QLabel, QCheckBox, QPushButton)
from PyQt5.QtCore import Qt, QRect
from siriushla.widgets import SiriusDialog, SiriusLedState
from pydm.widgets.base import PyDMWidget, PyDMWritableWidget

NR_BPMs = 160
NR_CHs = 120
NR_CVs = 160


class _PyDMCheckBoxList(PyDMWritableWidget, QWidget):

    def __init__(self, parent=None, init_channel=None, size=0):
        QWidget.__init__(self, parent=parent)
        PyDMWritableWidget.__init__(self, init_channel=init_channel)
        self.setVisible(False)
        self.cb_list = [QCheckBox() for _ in range(size)]
        self.btn_send = QPushButton('Apply Changes')
        self.btn_send.clicked.connect(self.send_value)
        self.btn_enbl_all = QPushButton('Enable All')
        self.btn_enbl_all.clicked.connect(_part(self.toogle_all, True))
        self.btn_dsbl_all = QPushButton('Disable All')
        self.btn_dsbl_all.clicked.connect(_part(self.toogle_all, False))

    def toogle_all(self, value):
        for cbx in self.cb_list:
            cbx.setChecked(bool(value))

    def send_value(self):
        if self.value is None:
            return
        value = np.array(
            [cbx.isChecked() for cbx in self.cb_list], dtype=bool)
        self.send_value_signal[np.ndarray].emit(value)

    def value_changed(self, new_val):
        super(_PyDMCheckBoxList, self).value_changed(new_val)
        for i, checked in enumerate(self.value):
            self.cb_list[i].setChecked(checked)

    def connection_changed(self, new_val):
        super(_PyDMCheckBoxList, self).connection_changed(new_val)
        for cbx in self.cb_list:
            cbx.setEnabled(new_val)


class _PyDMLedList(PyDMWidget, QWidget):

    def __init__(self, parent=None, init_channel=None, size=0):
        QWidget.__init__(self, parent=parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.setVisible(False)
        self.led_list = []
        sz_polc = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for _ in range(size):
            led = SiriusLedState()
            led.setSizePolicy(sz_polc)
            self.led_list.append(led)

    def value_changed(self, new_val):
        super(_PyDMLedList, self).value_changed(new_val)
        for i, checked in enumerate(self.value):
            self.led_list[i].setState(checked)

    def connection_changed(self, new_val):
        super(_PyDMLedList, self).connection_changed(new_val)
        for led in self.led_list:
            led.setEnabled(new_val)


class SelectionMatrix(QWidget):
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
        self.pv_sp = _PyDMCheckBoxList(
            parent=self,
            init_channel=self.prefix + self.dev + 'EnblList-SP',
            size=self.INDICES_LENGTH[self.dev])
        self.pv_rb = _PyDMLedList(
            parent=self,
            init_channel=self.prefix + self.dev + 'EnblList-RB',
            size=self.INDICES_LENGTH[self.dev])
        self._setup_ui()

    def _setup_ui(self):
        name = self.dev + "List"
        self.setObjectName(name)
        grid_l = QGridLayout(self)

        lab = QLabel(name, self)
        lab.setStyleSheet("font: 20pt \"Sans Serif\";\nfont-weight: bold;")
        lab.setAlignment(Qt.AlignCenter)
        grid_l.addWidget(lab, 0, 0, 1, 1)

        scr_ar = QScrollArea(self)
        grid_l.addWidget(scr_ar, 1, 0, 1, 1)
        scr_ar.setWidgetResizable(True)
        scr_ar_wid = QWidget()
        scr_ar_wid.setGeometry(QRect(0, 0, 1892, 1355))
        scr_ar.setWidget(scr_ar_wid)
        vbl = QVBoxLayout(scr_ar_wid)
        vbl.setContentsMargins(0, 0, 0, 0)
        wid = self._create_matrix(scr_ar_wid)
        vbl.addWidget(wid)

        wid = QWidget(scr_ar_wid)
        grid_l.addWidget(wid, 2, 0, 1, 1)
        hbl = QHBoxLayout(wid)
        hbl.addWidget(self.pv_sp.btn_dsbl_all)
        hbl.addWidget(self.pv_sp.btn_enbl_all)
        hbl.addWidget(self.pv_sp.btn_send)
        grid_l.setSizeConstraint(grid_l.SetMinimumSize)

    def _create_matrix(self, parent):
        wid = QWidget(parent)
        wid.setStyleSheet("font: 16pt \"Sans Serif\";\nfont-weight: bold;")
        vbl = QVBoxLayout(wid)

        subsecs, indices = self._get_matrix_params()
        secs = ['{0:02d}'.format(i+1) for i in range(20)]
        len_ = len(subsecs)

        wid2 = self._make_line('00', subsecs, list(range(len_)), True)
        vbl.addWidget(wid2)
        for i, sec in enumerate(secs):
            wid2 = self._make_line(sec, subsecs,
                                   indices[i*len_:(i+1)*len_], False)
            vbl.addWidget(wid2)
        return wid

    def _get_matrix_params(self):
        max_idx = self.INDICES_LENGTH[self.dev] - 1
        indices = list(range(max_idx))
        indices = [max_idx, ] + indices
        return self.SUBSECTIONS[self.dev], indices

    def _make_line(self, section, subsections, indices, header):
        label = section+self.dev
        wid = QWidget()
        if int(section) % 2:
            wid.setStyleSheet('background-color: rgb(220, 220, 220);')
        wid.setObjectName('Wid_'+label)
        hbl = QHBoxLayout(wid)
        hbl.setObjectName('HL_'+label)
        hspace = QSpacerItem(40, 20,
                             QSizePolicy.Expanding, QSizePolicy.Minimum)
        hbl.addItem(hspace)
        lab = QLabel(wid)
        lab.setObjectName('LB_'+label)
        lab.setText('  ' if header else section)
        hbl.addWidget(lab)
        hspace = QSpacerItem(40, 20,
                             QSizePolicy.Expanding, QSizePolicy.Minimum)
        hbl.addItem(hspace)
        for subsection, index in zip(subsections, indices):
            if header:
                lab = QLabel(wid)
                lab.setObjectName('LB_' + self.dev+subsection)
                lab.setText(subsection)
                hbl.addWidget(lab)
            else:
                subhl = self._make_unit(wid, section, subsection, index)
                hbl.addLayout(subhl)
            hspace = QSpacerItem(40, 20,
                                 QSizePolicy.Expanding, QSizePolicy.Minimum)
            hbl.addItem(hspace)
        return wid

    def _make_unit(self, parent, section, subsection, index):
        label = self.dev+section+subsection
        hbl = QHBoxLayout()
        hbl.setObjectName('HL_'+label)
        cbx = self.pv_sp.cb_list[index]
        cbx.setParent(parent)
        cbx.setToolTip(label)
        hbl.addWidget(cbx)

        led = self.pv_rb.led_list[index]
        led.setParent(parent)
        led.setToolTip(label)
        hbl.addWidget(led)
        return hbl


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    wid = SelectionMatrix(win, 'BPMX', 'ca://' + pref+'SI-Glob:AP-SOFB:')
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriuspy.envars import vaca_prefix as pref
    import sys

    _main()
