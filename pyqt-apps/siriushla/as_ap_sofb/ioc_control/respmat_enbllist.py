"""Create the Selection Matrices for BPMs and Correctors."""

from functools import partial as _part
import numpy as np
from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QScrollArea, QWidget, QPushButton, QDialog, QTabWidget
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

    def __init__(
            self, parent=None, init_channel=None, chan_otpl=None, size=0,
            side_headers=[], top_headers=[]):
        self.side_headers_wids = side_headers
        self.top_headers_wids = top_headers
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
        for i in range(value.size):
            led = self.led_list[i]
            if led.isSelected():
                value[i] = not value[i]
                led.setSelected(False)
        self.pv_sp.send_value_signal[np.ndarray].emit(value)
        if other:
            self.pv_otpl.send_value_signal[np.ndarray].emit(value)

    def value_changed(self, new_val):
        super(_PyDMLedList, self).value_changed(new_val)
        for i, led in enumerate(self.led_list):
            if i < self.value.size:
                led.setVisible(True)
                led.state = not self.value[i]
            else:
                led.setVisible(False)
        rsize = self.value.size / len(self.led_list)
        ini = int(len(self.side_headers_wids) * rsize)
        for i, head in enumerate(self.side_headers_wids):
            head.setVisible(i < ini)
        self.adjustSize()
        parent = self.parent()
        while parent is not None:
            parent.adjustSize()
            if isinstance(parent, QDialog):
                break
            parent = parent.parent()

    def connection_changed(self, new_val):
        super(_PyDMLedList, self).connection_changed(new_val)
        for led in self.led_list:
            led.setEnabled(new_val)


class SelectionMatrix(BaseWidget):

    def __init__(self, parent, prefix, acc='SI'):
        super().__init__(parent, prefix, acc)
        tab = QTabWidget(self)
        QHBoxLayout(self).addWidget(tab)

        for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
            tab.addTab(
                SingleSelMatrix(tab, dev, self.prefix, acc=self.acc), dev)


class SingleSelMatrix(BaseWidget):
    """Create the Selection Matrices for BPMs and Correctors."""

    def __init__(self, parent, dev, prefix, acc='SI'):
        """Initialize the matrix of the specified dev."""
        super().__init__(parent, prefix, acc)
        self.setObjectName(acc.upper()+'App')
        self.dev = dev
        max_rz = self._csorb.MAX_RINGSZ
        bpms = np.array(self._csorb.BPM_POS)
        bpm_pos = [bpms + i*self._csorb.C0 for i in range(max_rz)]
        bpm_pos = np.hstack(bpm_pos)
        bpm_name = self._csorb.BPM_NAMES * max_rz
        bpm_nknm = self._csorb.BPM_NICKNAMES * max_rz
        self.devpos = {
            'BPMX': bpm_pos,
            'BPMY': bpm_pos,
            'CH': self._csorb.CH_POS,
            'CV': self._csorb.CV_POS}
        self.devotpl = {
            'BPMX': 'BPMY', 'BPMY': 'BPMX', 'CH': 'CV', 'CV': 'CH'}
        self.devnames = {
            'BPMX': (bpm_name, bpm_nknm),
            'BPMY': (bpm_name, bpm_nknm),
            'CH': (self._csorb.CH_NAMES, self._csorb.CH_NICKNAMES),
            'CV': (self._csorb.CV_NAMES, self._csorb.CV_NICKNAMES)}
        self._get_headers()
        self.prefix = prefix
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
            side_headers = [' ']
        self.top_headers = top_headers
        self.side_headers = side_headers
        if self.dev.lower().startswith('bpm'):
            self.side_headers *= self._csorb.MAX_RINGSZ

        side_headers_wids = []
        top_headers_wids = []
        for i, head in enumerate(self.top_headers):
            head_wid = QLabel(head, alignment=Qt.AlignCenter)
            top_headers_wids.append(head_wid)
        for i, head in enumerate(self.side_headers):
            head_wid = QLabel(head, alignment=Qt.AlignCenter)
            side_headers_wids.append(head_wid)
        self.top_headers_wids = top_headers_wids
        self.side_headers_wids = side_headers_wids

    def _setup_ui(self):
        name = self.dev + "List"
        grid_l = QGridLayout(self)

        lab = QLabel(name, self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        grid_l.addWidget(lab, 0, 0, 1, 1)

        scr_ar = QScrollArea(self)
        grid_l.addWidget(scr_ar, 1, 0, 1, 1)
        scr_ar.setWidgetResizable(True)
        scr_ar_wid = QWidget()
        scr_ar_wid.setObjectName('scrollarea')
        scr_ar_wid.setStyleSheet(
            '#scrollarea {background-color: transparent;}')
        scr_ar.setWidget(scr_ar_wid)
        vbl = QVBoxLayout(scr_ar_wid)
        vbl.setContentsMargins(0, 0, 0, 0)

        self.pvs = _PyDMLedList(
            parent=scr_ar_wid,
            init_channel=self.prefix + self.dev + 'EnblList-RB',
            chan_otpl=self.prefix + self.devotpl[self.dev] + 'EnblList-RB',
            size=len(self.devnames[self.dev][0]),
            side_headers=self.side_headers_wids,
            top_headers=self.top_headers_wids)
        wid = self._create_matrix(scr_ar_wid)
        vbl.addWidget(wid)

        wid = QWidget(self)
        wid.setObjectName('scrollarea')
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
        self.pvs.setParent(wid)
        gdl = QGridLayout(wid)

        for i, head in enumerate(self.top_headers_wids):
            head.setParent(wid)
            gdl.addWidget(head, 0, i+1)
        for i, head in enumerate(self.side_headers_wids):
            head.setParent(wid)
            gdl.addWidget(head, i+1, 0)
        for idx in range(len(self.devnames[self.dev][0])):
            wid2 = self._make_unit(wid, idx)
            i, j = self._get_position(idx)
            gdl.addWidget(wid2, i+1, j+1)
        return wid

    def _get_position(self, idx):
        _, nicks = self.devnames[self.dev]
        rsize, hsize, i = len(nicks), len(self.side_headers), 0
        if self.dev.lower().startswith('bpm'):
            rsize //= self._csorb.MAX_RINGSZ
            hsize //= self._csorb.MAX_RINGSZ
            i = (idx // rsize) * hsize
        if self.acc == 'BO':
            sec = int(nicks[idx][:2])
            j = ((sec-1) % 10) + 1
            j = self.top_headers.index('{0:02d}'.format(j))
            if not (idx+1) % rsize and sec == 1:
                i += hsize - 1
            else:
                i += (sec-1) // 10
        elif self.acc == 'SI':
            j = self.top_headers.index(nicks[idx][2:])
            if not (idx+1) % rsize:
                i += hsize-1
            else:
                i += ((idx % rsize) + 1) // len(self.top_headers)
        else:
            j = idx
        return i, j

    def _make_unit(self, parent, index):
        label = self.devnames[self.dev][1][index]
        label += '; Pos = {0:5.1f} m'.format(self.devpos[self.dev][index])
        wid = QWidget(parent)
        hbl = QHBoxLayout(wid)
        led = self.pvs.led_list[index]
        led.setParent(wid)
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
        for i, led in enumerate(self.led_list):
            if not led.isVisible():
                continue
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
    acc = 'BO'
    widb = SelectionMatrix(win, 'BPMX', pref+acc+'-Glob:AP-SOFB:', acc)
    widh = SelectionMatrix(win, 'CH', pref+acc+'-Glob:AP-SOFB:', acc)
    widv = SelectionMatrix(win, 'CV', pref+acc+'-Glob:AP-SOFB:', acc)
    hbl.addWidget(widb)
    hbl.addWidget(widh)
    hbl.addWidget(widv)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import VACA_PREFIX as pref
    import sys

    _main()
