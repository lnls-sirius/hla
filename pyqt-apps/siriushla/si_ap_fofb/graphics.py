"""Graphics module."""

import numpy as _np

from qtpy.QtWidgets import QToolTip, QWidget

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.fofb.csdev import HLFOFBConst

from ..widgets import SiriusConnectionSignal as _ConnSig
from ..as_ap_sofb.graphics.respmat import ShowMatrixWidget as _ShowMatrixWidget


class ShowMatrixWidget(_ShowMatrixWidget):

    def __init__(self, parent, device, prefix=''):
        QWidget.__init__(self, parent)
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self.acc = 'SI'
        self.setObjectName('SIApp')
        self._csorb = HLFOFBConst()
        self._inflines = []
        self.setupui()
        self.mat = _ConnSig(self.devpref.substitute(propty='RespMat-Mon'))
        self.mat.new_value_signal[_np.ndarray].connect(self._update_graph)
        self._update_graph(None)

    def _show_tooltip(self, pos):
        names = self._csorb.bpm_nicknames
        cname = self._csorb.ch_nicknames + self._csorb.cv_nicknames + ['RF', ]
        posi = self._csorb.bpm_pos

        graph = self.graph
        curve = graph.curveAtIndex(0)
        posx = curve.scatter.mapFromScene(pos).x()
        ind = _np.argmin(_np.abs(_np.array(posi)-posx))
        posy = curve.scatter.mapFromScene(pos).y()

        indy = int(posy // self.spbox.value())
        indy = max(min(indy, len(cname)-1), 0)
        txt = 'BPM = {0:s}, Corr = {1:s}'.format(names[ind], cname[indy])
        QToolTip.showText(
            graph.mapToGlobal(pos.toPoint()),
            txt, graph, graph.geometry(), 500)

    def _update_graph(self, *args):
        sep = self.spbox.value()
        val = self.mat.value
        if val is None:
            return
        val = val.reshape(-1, self._csorb.nr_corrs)
        for i in range(self._csorb.nr_corrs):
            cur = self.graph.curveAtIndex(i)
            cur.receiveYWaveform(sep*i + val[:, i])
