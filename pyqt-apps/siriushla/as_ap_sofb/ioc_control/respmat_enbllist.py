"""Create the Selection Matrices for BPMs and Correctors."""

from functools import partial as _part
import numpy as np
from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, \
    QSizePolicy, QScrollArea, QWidget, QLabel, QCheckBox, QPushButton
from qtpy.QtCore import Qt, QRect, QPoint
from qtpy.QtGui import QBrush, QColor, QPainter
from siriushla.widgets import SiriusLedAlert, SiriusConnectionSignal
from pydm.widgets.base import PyDMWidget
# import siriuspy.csdevice.orbitcorr as _csorb


class Led(SiriusLedAlert):

    def mouseReleaseEvent(self, _):
        self.toggle()

    def toggle(self):
        self.setSelected(not self.isSelected())


class _PyDMLedList(PyDMWidget, QWidget):

    def __init__(self, parent=None, init_channel=None, size=0):
        QWidget.__init__(self, parent=parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.pv_sp = SiriusConnectionSignal(init_channel.replace('-RB', '-SP'))
        self.setVisible(False)
        self.btn_send = QPushButton('Apply Changes')
        self.btn_send.clicked.connect(self.send_value)
        self.btn_enbl_all = QPushButton('Enable All')
        self.btn_enbl_all.clicked.connect(_part(self.toogle_all, True))
        self.btn_dsbl_all = QPushButton('Disable All')
        self.btn_dsbl_all.clicked.connect(_part(self.toogle_all, False))
        self.btn_unsel_all = QPushButton('Undo Selection')
        self.btn_unsel_all.clicked.connect(self.undo_selection)

        self.led_list = []
        sz_polc = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for _ in range(size):
            led = Led()
            led.setSizePolicy(sz_polc)
            self.led_list.append(led)

    def channels(self):
        chans = super().channels()
        chans.append(self.pv_sp)
        return chans

    def undo_selection(self, _):
        for led in self.led_list:
            led.setSelected(False)

    def toogle_all(self, value):
        for led in self.led_list:
            if not (bool(led.state) != value):
                led.setSelected(True)

    def send_value(self):
        if self.value is None:
            return
        value = self.value.copy()
        for i, led in enumerate(self.led_list):
            if led.isSelected():
                value[i] = not value[i]
                led.setSelected(False)
        self.pv_sp.send_value_signal[np.ndarray].emit(value)

    def value_changed(self, new_val):
        super(_PyDMLedList, self).value_changed(new_val)
        for i, checked in enumerate(self.value):
            self.led_list[i].state = not checked

    def connection_changed(self, new_val):
        super(_PyDMLedList, self).connection_changed(new_val)
        for led in self.led_list:
            led.setEnabled(new_val)


class SelectionMatrix(QWidget):
    """Create the Selection Matrices for BPMs and Correctors."""

    def __init__(self, parent, dev, prefix, acc='SI'):
        """Initialize the matrix of the specified dev."""
        super().__init__(parent)
        self.acc = acc
        self._select_ring(acc)
        self.prefix = prefix
        self.dev = dev
        self.pvs = _PyDMLedList(
            parent=self,
            init_channel=self.prefix + self.dev + 'EnblList-RB',
            size=self.INDICES_LENGTH[self.dev])
        self._setup_ui()

    def _select_ring(self, acc):
        if acc.lower() == 'si':
            NR_BPMs = 160
            NR_CHs = 120
            NR_CVs = 160
            self.SUBSECTIONS = {
                'BPMX': (
                    'M1', 'M2', 'C1-1', 'C1-2', 'C2', 'C3-1', 'C3-2', 'C4'),
                'BPMY': (
                    'M1', 'M2', 'C1-1', 'C1-2', 'C2', 'C3-1', 'C3-2', 'C4'),
                'CV':   (
                    'M1', 'M2', 'C1', 'C2-1', 'C2-2', 'C3-1', 'C3-2', 'C4'),
                'CH':   (
                    'M1', 'M2', 'C1', 'C2', 'C3', 'C4')}
            self.SECTIONS = ['{0:02d}'.format(i+1) for i in range(20)]
        else:
            NR_BPMs = 50
            NR_CHs = 25
            NR_CVs = 25
            self.SUBSECTIONS = {
                'BPMX': ('', '', '', '', ''),
                'BPMY': ('', '', '', '', ''),
                'CV':   ('', '', '', '', ''),
                'CH':   ('', '', '', '', '')}
            self.SECTIONS = [
                '01-05', '06-10',
                '11-15', '16-20',
                '21-25', '26-30',
                '31-35', '36-40',
                '41-45', '46-50']
        self.INDICES_LENGTH = {
            'BPMX': NR_BPMs, 'BPMY': NR_BPMs, 'CH': NR_CHs, 'CV': NR_CVs}

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
        hbl.addWidget(self.pvs.btn_dsbl_all)
        hbl.addWidget(self.pvs.btn_enbl_all)
        hbl.addWidget(self.pvs.btn_send)
        grid_l.setSizeConstraint(grid_l.SetMinimumSize)

    def _create_matrix(self, parent):
        wid = MyWidget(self.pvs.led_list, parent)
        wid.setStyleSheet("font: 16pt \"Sans Serif\";\nfont-weight: bold;")
        gdl = QGridLayout(wid)
        gdl.setSpacing(20)
        # gdl.setColumnMinimumWidth(30)

        secs, subsecs, indices = self._get_matrix_params()
        len_ = len(subsecs)

        self._make_line(gdl, 0, '00', subsecs, list(range(len_)), True)
        for i, sec in enumerate(secs):
            self._make_line(
                gdl, i+1, sec, subsecs, indices[i*len_:(i+1)*len_], False)
        return wid

    def _get_matrix_params(self):
        max_idx = self.INDICES_LENGTH[self.dev] - 1
        indices = list(range(max_idx))
        indices = [max_idx, ] + indices
        return self.SECTIONS, self.SUBSECTIONS[self.dev], indices

    def _make_line(self, gdl, idx, section, subsections, indices, header):
        label = section+self.dev
        lab = QLabel(self)
        lab.setText('  ' if header else section)
        lab.setAlignment(Qt.AlignCenter)
        j = 0
        gdl.addWidget(lab, idx, 0)
        j += 1
        for subsection, index in zip(subsections, indices):
            if header:
                lab = QLabel(self)
                lab.setText(subsection)
                lab.setAlignment(Qt.AlignCenter)
                gdl.addWidget(lab, idx, j)
            else:
                wid = self._make_unit(self, section, subsection, index)
                gdl.addWidget(wid, idx, j)
            j += 1

    def _make_unit(self, parent, section, subsection, index):
        label = ''
        if self.acc.lower() == 'si':
            label = section+subsection
        wid = QWidget(parent)
        hbl = QHBoxLayout(wid)
        led = self.pvs.led_list[index]
        led.setParent(wid)
        led.setToolTip('{0:d}'.format(index))
        led.setToolTip(label)
        hbl.addWidget(led)
        return wid


class MyWidget(QWidget):
    def __init__(self, led_list, parent=None):
        super().__init__(parent)
        self.led_list = led_list
        self.begin = QPoint()
        self.end = QPoint()

    def _paint(self):
        if self.begin == self.end:
            return
        qp = QPainter(self)
        br = QBrush(QColor(100, 10, 10, 40))
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin, self.end))

    def paintEvent(self, _):
        self._paint()

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.selectitems()
        self.begin = event.pos()
        self.update()

    def selectitems(self):
        for led in self.led_list:
            pos = led.mapTo(self, led.pos())
            sz = led.size()
            x1 = pos.x()+sz.width()/2 > self.begin.x()  # Mistery:factor of 2
            x2 = pos.x()+sz.width()/2 > self.end.x()
            y1 = pos.y()+sz.height()/2 > self.begin.y()
            y2 = pos.y()+sz.height()/2 > self.end.y()
            if x1 != x2 and y1 != y2:
                led.toggle()


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    wid = SelectionMatrix(win, 'BPMX', 'ca://' + pref+'SI-Glob:AP-SOFB:', 'BO')
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys

    _main()
