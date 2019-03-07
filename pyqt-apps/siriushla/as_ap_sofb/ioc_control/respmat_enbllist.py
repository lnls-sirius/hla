"""Create the Selection Matrices for BPMs and Correctors."""

from functools import partial as _part
import numpy as np
from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QScrollArea, QWidget, QPushButton
from qtpy.QtCore import Qt, QRect, QPoint
from qtpy.QtGui import QBrush, QColor, QPainter
from siriushla.widgets import SiriusLedAlert, SiriusConnectionSignal
from pydm.widgets.base import PyDMWidget
from siriushla.as_ap_sofb.ioc_control.base import BaseWidget


class Led(SiriusLedAlert):

    def mouseReleaseEvent(self, _):
        self.toggle()

    def toggle(self):
        self.setSelected(not self.isSelected())


class _PyDMLedList(PyDMWidget, QWidget):

    def __init__(self, parent=None, init_channel=None, chan_otpl=None, size=0):
        QWidget.__init__(self, parent=parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.pv_sp = SiriusConnectionSignal(init_channel.replace('-RB', '-SP'))
        self.pv_otpl = SiriusConnectionSignal(chan_otpl.replace('-RB', '-SP'))
        self.setVisible(False)
        self.btn_send = QPushButton('Apply Changes')
        self.btn_send.clicked.connect(self.send_value)
        self.btn_send_otpl = QPushButton('Apply Both Planes')
        self.btn_send_otpl.clicked.connect(_part(self.send_value, other=True))
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

    def send_value(self, other=False):
        if self.value is None:
            return
        value = self.value.copy()
        for i, led in enumerate(self.led_list):
            if led.isSelected():
                value[i] = not value[i]
                led.setSelected(False)
        self.pv_sp.send_value_signal[np.ndarray].emit(value)
        if other:
            self.pv_otpl.send_value_signal[np.ndarray].emit(value)

    def value_changed(self, new_val):
        super(_PyDMLedList, self).value_changed(new_val)
        for i, checked in enumerate(self.value):
            self.led_list[i].state = not checked

    def connection_changed(self, new_val):
        super(_PyDMLedList, self).connection_changed(new_val)
        for led in self.led_list:
            led.setEnabled(new_val)


class SelectionMatrix(BaseWidget):
    """Create the Selection Matrices for BPMs and Correctors."""

    def __init__(self, parent, dev, prefix, acc='SI'):
        """Initialize the matrix of the specified dev."""
        super().__init__(parent, prefix, acc)
        self.dev = dev
        self.devpos = {
            'BPMX': self._csorb.BPM_POS,
            'BPMY': self._csorb.BPM_POS,
            'CH': self._csorb.CH_POS,
            'CV': self._csorb.CV_POS}
        self.devotpl = {
            'BPMX': 'BPMY', 'BPMY': 'BPMX', 'CH': 'CV', 'CV': 'CH'}
        self.devnames = {
            'BPMX': (self._csorb.BPM_NAMES, self._csorb.BPM_NICKNAMES),
            'BPMY': (self._csorb.BPM_NAMES, self._csorb.BPM_NICKNAMES),
            'CH': (self._csorb.CH_NAMES, self._csorb.CH_NICKNAMES),
            'CV': (self._csorb.CV_NAMES, self._csorb.CV_NICKNAMES)}
        self._get_headers()
        self.prefix = prefix
        self.pvs = _PyDMLedList(
            parent=self,
            init_channel=self.prefix + self.dev + 'EnblList-RB',
            chan_otpl=self.prefix + self.devotpl[self.dev] + 'EnblList-RB',
            size=len(self.devnames[self.dev][0]))
        self._setup_ui()

    def _get_headers(self):
        _, nicks = self.devnames[self.dev]
        if self.acc == 'BO':
            top_headers = ['{0:02d}'.format(i) for i in range(1, 11)]
            if self.dev.startswith('C'):
                top_headers = top_headers[::2]
            side_headers = [
                '01-10', '11-20', '21-30', '31-40', '41-50', '01-10']
            if nicks[-1][:2] != '01':
                side_headers = side_headers[:-1]
        elif self.acc == 'SI':
            top_headers = sorted({nick[2:] for nick in nicks})
            top_headers = top_headers[-2:] + top_headers[:-2]
            side_headers = sorted({nick[:2] for nick in nicks})
            side_headers.append(side_headers[0])
        else:
            top_headers = nicks
            side_headers = []
        self.side_headers = side_headers
        self.top_headers = top_headers

    def _setup_ui(self):
        name = self.dev + "List"
        self.setObjectName(name)
        grid_l = QGridLayout(self)

        lab = QLabel(name, self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        grid_l.addWidget(lab, 0, 0, 1, 1)

        scr_ar = QScrollArea(self)
        grid_l.addWidget(scr_ar, 1, 0, 1, 1)
        scr_ar.setWidgetResizable(True)
        scr_ar_wid = QWidget()
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
        if self.dev.lower().startswith('bpm'):
            hbl.addWidget(self.pvs.btn_send_otpl)
        grid_l.setSizeConstraint(grid_l.SetMinimumSize)

    def _create_matrix(self, parent):
        wid = MyWidget(self.pvs.led_list, parent)
        wid.setStyleSheet("font-weight: bold;")
        gdl = QGridLayout(wid)

        for i, head in enumerate(self.top_headers):
            gdl.addWidget(QLabel(head, wid, alignment=Qt.AlignCenter), 0, i+1)
        for i, head in enumerate(self.side_headers):
            gdl.addWidget(QLabel(head, wid, alignment=Qt.AlignCenter), i+1, 0)
        for dev in self.devnames[self.dev][0]:
            wid2, idx = self._make_unit(wid, dev)
            i, j = self._get_position(idx)
            gdl.addWidget(wid2, i+1, j+1)
        return wid

    def _get_position(self, idx):
        _, nicks = self.devnames[self.dev]
        if self.acc == 'BO':
            sec = int(nicks[idx][:2])
            j = ((sec-1) % 10) + 1
            j = self.top_headers.index('{0:02d}'.format(j))
            i = (sec-1) // 10
            if idx == len(nicks)-1 and sec == 1:
                i = len(self.side_headers) - 1
        elif self.acc == 'SI':
            j = self.top_headers.index(nicks[idx][2:])
            i = (idx+1) // len(self.top_headers)
            if idx == len(nicks)-1:
                i = len(self.side_headers)-1
        else:
            i, j = 0, idx
        return i, j

    def _make_unit(self, parent, dev):
        index = self.devnames[self.dev][0].index(dev)
        label = self.devnames[self.dev][1][index]
        label += '; Pos = {0:5.1f} m'.format(self.devpos[self.dev][index])
        wid = QWidget(parent)
        hbl = QHBoxLayout(wid)
        led = self.pvs.led_list[index]
        led.setParent(wid)
        led.setToolTip(label)
        hbl.addWidget(led)
        return wid, index


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
            x1 = pos.x()+sz.width()/2 > self.begin.x()
            x2 = pos.x()+sz.width()/2 > self.end.x()
            y1 = pos.y()+sz.height()/2 > self.begin.y()
            y2 = pos.y()+sz.height()/2 > self.end.y()
            if x1 != x2 and y1 != y2:
                led.toggle()


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    acc = 'TB'
    wid = SelectionMatrix(win, 'CV', pref+acc+'-Glob:AP-SOFB:', acc)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys

    _main()
