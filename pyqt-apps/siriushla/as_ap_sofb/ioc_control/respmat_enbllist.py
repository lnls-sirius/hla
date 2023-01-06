"""Create the Selection Matrices for BPMs and Correctors."""

from functools import partial as _part

import numpy as np

from qtpy.QtCore import QSize
from qtpy.QtWidgets import QHBoxLayout, \
    QSizePolicy, QWidget, QDialog, QTabWidget

from pydm.widgets.base import PyDMWidget

from siriushla.widgets import SiriusLedAlert, QLed, \
    SiriusConnectionSignal as _ConnSignal, \
    SelectionMatrixWidget as SelectionWidget
from siriushla.as_ap_sofb.ioc_control.base import BaseObject, BaseWidget


class SingleSelMatrix(BaseObject, SelectionWidget, PyDMWidget):
    """Create the Selection Matrices for BPMs and Correctors."""

    def __init__(self, parent, dev, device, prefix='', acc='SI'):
        """Initialize the matrix data of the specified dev."""

        # initialize BaseObject
        BaseObject.__init__(self, device, prefix=prefix, acc=acc)
        self.dev = dev
        bpm_pos = np.array(self._csorb.bpm_pos)
        bpm_name = self._csorb.bpm_names
        bpm_nknm = self._csorb.bpm_nicknames
        self.devpos = {
            'BPMX': bpm_pos,
            'BPMY': bpm_pos,
            'CH': self._csorb.ch_pos,
            'CV': self._csorb.cv_pos}
        self.devotpl = {
            'BPMX': 'BPMY', 'BPMY': 'BPMX', 'CH': 'CV', 'CV': 'CH'}
        self.devnames = {
            'BPMX': (bpm_name, bpm_nknm),
            'BPMY': (bpm_name, bpm_nknm),
            'CH': (self._csorb.ch_names, self._csorb.ch_nicknames),
            'CV': (self._csorb.cv_names, self._csorb.cv_nicknames)}

        # initialize SelectionWidget
        SelectionWidget.__init__(
            self, parent=parent, title=dev + "List",
            has_bothplanes=dev.lower().startswith('bpm'))

        # initialize PyDMWidget
        init_channel = self.devpref.substitute(propty=self.dev+'EnblList-RB')
        PyDMWidget.__init__(self, init_channel=init_channel)

        self.pv_sp = _ConnSignal(init_channel.replace('-RB', '-SP'))
        self.pv_otpl = _ConnSignal(self.devpref.substitute(
            propty=self.devotpl[self.dev]+'EnblList-SP'))

        # connect signals and slots
        self.applyChangesClicked.connect(self.send_value)
        self.applyBothPlanesClicked.connect(_part(self.send_value, other=True))

    def sizeHint(self):
        """Return the base size of the widget."""
        return QSize(500, 1200)

    # --- SelectionWidget specific methods ---

    def get_headers(self):
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
        return top_headers, side_headers

    def get_widgets(self):
        widgets = list()
        sz_polc = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for idx in range(len(self.devnames[self.dev][0])):
            wid = QWidget(self.parent())
            led = SiriusLedAlert()
            led.setParent(wid)
            led.setSizePolicy(sz_polc)
            tooltip = self.devnames[self.dev][1][idx]
            tooltip += '; Pos = {0:5.1f} m'.format(self.devpos[self.dev][idx])
            led.setToolTip(tooltip)
            hbl = QHBoxLayout(wid)
            hbl.setContentsMargins(0, 0, 0, 0)
            hbl.addWidget(led)
            widgets.append(wid)
        return widgets

    def get_positions(self):
        top_headers, side_headers = self.headers
        positions = list()
        for idx in range(len(self.devnames[self.dev][0])):
            _, nicks = self.devnames[self.dev]
            rsize, hsize, i = len(nicks), len(side_headers), 0
            if self.dev.lower().startswith('bpm'):
                i = (idx // rsize) * hsize
            if self.acc == 'BO':
                sec = int(nicks[idx][:2])
                j = ((sec-1) % 10) + 1
                j = top_headers.index('{0:02d}'.format(j))
                if not (idx+1) % rsize and sec == 1:
                    i += hsize - 1
                else:
                    i += (sec-1) // 10
            elif self.acc == 'SI':
                j = top_headers.index(nicks[idx][2:])
                if not (idx+1) % rsize:
                    i += hsize-1
                else:
                    i += ((idx % rsize) + 1) // len(top_headers)
            else:
                j = idx
            positions.append((i, j))
        return positions

    # --- PyDMWidget specific methods ---

    def send_value(self, other=False):
        if self.value is None:
            return
        value = self.value.copy()
        for i in range(value.size):
            wid = self.widgets[i]
            led = wid.findChild(QLed)
            if led.isSelected():
                value[i] = not value[i]
                led.setSelected(False)
        self.pv_sp.send_value_signal[np.ndarray].emit(value)
        if other:
            self.pv_otpl.send_value_signal[np.ndarray].emit(value)

    def value_changed(self, new_val):
        if not isinstance(new_val, np.ndarray):
            return

        super(SingleSelMatrix, self).value_changed(new_val)

        _, side_header_wids = self.header_widgets
        for i, wid in enumerate(self.widgets):
            led = wid.findChild(QLed)
            if i < self.value.size:
                wid.setVisible(True)
                led.state = not self.value[i]
            else:
                wid.setVisible(False)
        rsize = self.value.size / len(self.widgets)
        ini = int(len(side_header_wids) * rsize)
        for i, head in enumerate(side_header_wids):
            head.setVisible(i < ini)
        self.adjustSize()
        parent = self.parent()
        while parent is not None:
            parent.adjustSize()
            if isinstance(parent, QDialog):
                break
            parent = parent.parent()

    def connection_changed(self, new_conn):
        super(SingleSelMatrix, self).connection_changed(new_conn)
        for wid in self.widgets:
            led = wid.findChild(QLed)
            led.setEnabled(new_conn)

class SelectionMatrix(BaseWidget):

    def __init__(self, parent, device, prefix='', acc='SI'):
        super().__init__(parent, device, prefix=prefix, acc=acc)
        tab = QTabWidget(self)
        hbl = QHBoxLayout(self)
        hbl.addWidget(tab)
        hbl.setContentsMargins(0, 0, 0, 0)

        for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
            wid = SingleSelMatrix(
                tab, dev, self.device, prefix=self.prefix, acc=self.acc)
            tab.addTab(wid, dev)
