"""Graphics module."""

import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QToolTip, QWidget, QVBoxLayout, QLabel, QHBoxLayout

from pyqtgraph import mkBrush

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.fofb.csdev import HLFOFBConst

from ..widgets import SiriusConnectionSignal as _ConnSig, QDoubleSpinBoxPlus
from ..as_ap_sofb.graphics.base import Graph


class ShowMatrixWidget(QWidget):

    def __init__(self, parent, device, propty, prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self.acc = 'SI'
        self.setObjectName('SIApp')
        self._csorb = HLFOFBConst()
        self._is_inv = 'Inv' in propty
        self._is_coeff = 'Coeff' in propty
        self._is_hw = 'Hw' in propty
        self.setupui()
        self.mat = _ConnSig(self.devpref.substitute(propty=propty))
        self.mat.new_value_signal[_np.ndarray].connect(self._update_graph)
        if self._is_coeff:
            self.gain = _ConnSig(self.devpref.substitute(propty='CorrGains-Mon'))
            self.gain.new_value_signal[_np.ndarray].connect(self._update_graph)
        self._update_graph(None)
        self._update_horizontal()

    def setupui(self):
        vbl = QVBoxLayout(self)

        if self._is_coeff:
            text = 'Corrector Coefficients and Gains'
        else:
            if self._is_inv:
                text = 'Inverse '
            else:
                text = 'Transpose of '
            text += 'Response Matrix'
            if self._is_hw:
                text += ' - Hardware Units'
            else:
                text += ' - Physics Units'

        lab = QLabel(text, self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)

        graph = Graph(self)
        vbl.addWidget(graph)

        self.spbox = QDoubleSpinBoxPlus(self)
        self.spbox.setMaximum(1000)
        self.spbox.setValue(80)
        self.spbox.setKeyboardTracking(False)
        self.spbox.editingFinished.connect(self._update_graph)

        hbl = QHBoxLayout()
        vbl.addItem(hbl)
        hbl.addWidget(QLabel('Lines spacing:', self))
        hbl.addWidget(self.spbox)
        hbl.addStretch()

        graph.setShowLegend(False)
        graph.setLabel('bottom', text='BPM Position', units='m')
        if self._is_coeff:
            yunits = 'count/m'
        else:
            if self._is_hw:
                yunits = 'count/m' if self._is_inv else 'm/count'
            else:
                yunits = 'rad/m' if self._is_inv else 'm/rad'
        graph.setLabel('left', text='Matrix', units=yunits)
        ncorr = self._csorb.nr_chcv if self._is_coeff else self._csorb.nr_corrs
        for i in range(ncorr):
            color = 'blue'
            if i >= self._csorb.nr_ch:
                color = 'red'
            if i >= self._csorb.nr_ch+self._csorb.nr_cv:
                color = 'black'
            symbolBrush = None
            if self._is_coeff:
                gainbrush = mkBrush(QColor(color))
                symbolBrush = [gainbrush] + self._csorb.nr_bpms*[None]
            opts = dict(
                y_channel='',
                x_channel='',
                name='',
                color=color,
                redraw_mode=2,
                lineStyle=1,
                lineWidth=1,
                symbol='o',
                symbolSize=10)
            graph.addChannel(**opts)
            curve = graph.curveAtIndex(i)
            curve.opts['symbolBrush'] = symbolBrush
        graph.plotItem.scene().sigMouseMoved.connect(self._show_tooltip)
        self.graph = graph

    def _show_tooltip(self, pos):
        bname = self._csorb.bpm_nicknames
        cname = self._csorb.ch_nicknames + self._csorb.cv_nicknames + ['RF', ]
        bpos = self._csorb.bpm_pos

        graph = self.graph
        curve = graph.curveAtIndex(0)
        posx = curve.scatter.mapFromScene(pos).x()
        ind = _np.argmin(_np.abs(_np.array(bpos)-posx))
        posy = curve.scatter.mapFromScene(pos).y()

        indy = int(posy // self.spbox.value())
        indy = max(min(indy, len(cname)-1), 0)
        txt = 'BPM = {0:s}, Corr = {1:s}'.format(bname[ind], cname[indy])
        QToolTip.showText(
            graph.mapToGlobal(pos.toPoint()),
            txt, graph, graph.geometry(), 500)

    def _update_graph(self, *args):
        sep = self.spbox.value()
        val = self.mat.value
        if val is None:
            return
        if self._is_inv:
            val = val.reshape(self._csorb.nr_corrs, -1)
        elif self._is_coeff:
            val = val.reshape(self._csorb.nr_chcv, -1)
            gain = self.gain.value
            if gain is None:
                return
            val = _np.hstack([gain[:, None], val])
        else:
            val = val.reshape(-1, self._csorb.nr_corrs)
        ncorr = self._csorb.nr_chcv if self._is_coeff else self._csorb.nr_corrs
        for i in range(ncorr):
            cur = self.graph.curveAtIndex(i)
            if self._is_inv or self._is_coeff:
                cur.receiveYWaveform(sep*i + val[i, :])
            else:
                cur.receiveYWaveform(sep*i + val[:, i])

    def _update_horizontal(self):
        bpm_pos = _np.array(self._csorb.bpm_pos)
        ncorr = self._csorb.nr_chcv if self._is_coeff else self._csorb.nr_corrs
        for i in range(ncorr):
            cur = self.graph.curveAtIndex(i)
            pos = bpm_pos
            if self._is_inv or self._is_coeff:
                pos = _np.hstack([-1, bpm_pos])
            cur.receiveXWaveform(pos)
