"""Enable lists."""

from functools import partial as _part

from qtpy.QtWidgets import QHBoxLayout, QTabWidget

from pydm.widgets.base import PyDMWidget

from ..widgets import SiriusConnectionSignal as _ConnSignal, \
    SelectionMatrixWidget as SelectionWidget
from ..as_ap_sofb.ioc_control.respmat_enbllist import \
    SingleSelMatrix as _SingleSelMatrix

from .base import BaseObject, BaseWidget


class SingleSelMatrix(_SingleSelMatrix, BaseObject):
    """Create the Selection Matrices for BPMs and Correctors."""

    def __init__(self, parent, dev, device, prefix=''):
        """Initialize the matrix data of the specified dev."""

        # initialize BaseObject
        BaseObject.__init__(self, device, prefix=prefix)
        self.dev = dev
        self.devpos = {
            'BPMX': self._csorb.bpm_pos,
            'BPMY': self._csorb.bpm_pos,
            'CH': self._csorb.ch_pos,
            'CV': self._csorb.cv_pos}
        self.devotpl = {
            'BPMX': 'BPMY', 'BPMY': 'BPMX', 'CH': 'CV', 'CV': 'CH'}
        self.devnames = {
            'BPMX': (self._csorb.bpm_names, self._csorb.bpm_nicknames),
            'BPMY': (self._csorb.bpm_names, self._csorb.bpm_nicknames),
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

    def get_headers(self):
        _, nicks = self.devnames[self.dev]
        top_headers = sorted({nick[2:] for nick in nicks})
        top_headers = top_headers[-2:] + top_headers[:-2]
        side_headers = sorted({nick[:2] for nick in nicks})
        side_headers.append(side_headers[0])
        return top_headers, side_headers

    def get_positions(self):
        top_headers, side_headers = self.headers
        positions = list()
        for idx in range(len(self.devnames[self.dev][0])):
            _, nicks = self.devnames[self.dev]
            rsize, hsize, i = len(nicks), len(side_headers), 0
            j = top_headers.index(nicks[idx][2:])
            if not (idx+1) % rsize:
                i += hsize-1
            else:
                i += ((idx % rsize) + 1) // len(top_headers)
            positions.append((i, j))
        return positions


class SelectionMatrix(BaseWidget):

    def __init__(self, parent, device, prefix=''):
        super().__init__(parent, device, prefix=prefix)
        tab = QTabWidget(self)
        hbl = QHBoxLayout(self)
        hbl.addWidget(tab)
        hbl.setContentsMargins(0, 0, 0, 0)

        for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
            wid = SingleSelMatrix(tab, dev, self.device, prefix=self.prefix)
            tab.addTab(wid, dev)
