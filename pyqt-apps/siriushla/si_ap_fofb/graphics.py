"""Graphics module."""

from functools import partial as _part
import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QToolTip, QWidget, QVBoxLayout, QLabel, QHBoxLayout

from ..widgets import SiriusConnectionSignal as _ConnSig, QDoubleSpinBoxPlus,\
    SiriusDialog
from ..as_ap_sofb.graphics.base import Graph
from .base import BaseObject


class MatrixWidget(BaseObject, QWidget):
    """Matrix widget."""

    def __init__(self, parent, device, propty, prefix=''):
        """Init."""
        BaseObject.__init__(self, device, prefix)
        QWidget.__init__(self, parent)
        self.setObjectName('SIApp')
        self._is_inv = 'Inv' in propty
        self._is_coeff = 'Coeff' in propty
        self._is_hw = 'Hw' in propty
        self._setupui()
        self.mat = _ConnSig(self.devpref.substitute(propty=propty))
        self.mat.new_value_signal[_np.ndarray].connect(self._update_graph)
        self._update_graph(None)
        self._update_horizontal()

    def _setupui(self):
        vbl = QVBoxLayout(self)

        if self._is_coeff:
            text = 'Corrector Coefficients'
        else:
            text = 'Inverse' if self._is_inv else 'Transpose'
            text += ' of Response Matrix - '
            text += 'Hardware Units' if self._is_hw else 'Physics Units'

        lab = QLabel(text, self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)

        graph = Graph(self)
        vbl.addWidget(graph)

        self.spbox = QDoubleSpinBoxPlus(self)
        self.spbox.setMinimum(0.01)
        self.spbox.setMaximum(1000)
        value = 1.0 if self._is_coeff or self._is_inv else 80.0
        self.spbox.setValue(value)
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
            yunits = 'count/nm'
        else:
            if self._is_hw:
                yunits = 'count/nm' if self._is_inv else 'nm/count'
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


class CorrGainWidget(BaseObject, QWidget):
    """Matrix widget."""

    def __init__(self, parent, device, prefix=''):
        """Init."""
        BaseObject.__init__(self, device, prefix)
        QWidget.__init__(self, parent)
        self.setObjectName('SIApp')
        self._setupui()
        self.gains = _ConnSig(self.devpref.substitute(propty='CorrGains-Mon'))
        self.gains.new_value_signal[_np.ndarray].connect(self._update_graph)
        self._update_horizontal()

    def _setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel('Corrector Gains', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)

        for plane in ['h', 'v']:
            graph = Graph(self)
            name = 'graph_' + plane
            setattr(self, name, graph)
            graph.setTitle('Horizontal' if plane == 'h' else 'Vertical')
            graph.setObjectName(name)
            graph.setStyleSheet('#'+name+'{min-width: 16em; min-height: 8em;}')
            graph.setLabel('bottom', text='Position', units='m')
            graph.setLabel('left', text='Gain')
            graph.showLegend = False
            color = 'blue' if plane == 'h' else 'red'
            opts = dict(
                y_channel='', x_channel='', name='',
                color=color, redraw_mode=2,
                lineStyle=1, lineWidth=1,
                symbol='o', symbolSize=10)
            graph.addChannel(**opts)
            graph.plotItem.scene().sigMouseMoved.connect(
                _part(self._show_tooltip, plane))
            vbl.addWidget(graph)

    def _show_tooltip(self, plane, pos):
        if plane == 'h':
            cname = self._csorb.ch_nicknames
            xdata = self._csorb.ch_pos
        else:
            cname = self._csorb.cv_nicknames
            xdata = self._csorb.cv_pos

        graph = getattr(self, 'graph_' + plane)
        curve = graph.curveAtIndex(0)
        posx = curve.scatter.mapFromScene(pos).x()
        ind = _np.argmin(_np.abs(_np.array(xdata)-posx))
        txt = '{0:s}'.format(cname[ind])
        QToolTip.showText(
            graph.mapToGlobal(pos.toPoint()),
            txt, graph, graph.geometry(), 500)

    def _update_graph(self, *args):
        val = self.gains.value
        if val is None:
            return
        curve = self.graph_h.curveAtIndex(0)
        curve.receiveYWaveform(_np.array(val[:self._csorb.nr_ch]))
        curve = self.graph_v.curveAtIndex(0)
        curve.receiveYWaveform(_np.array(val[self._csorb.nr_ch:]))

    def _update_horizontal(self):
        curve = self.graph_h.curveAtIndex(0)
        curve.receiveXWaveform(_np.array(self._csorb.ch_pos))
        curve = self.graph_v.curveAtIndex(0)
        curve.receiveXWaveform(_np.array(self._csorb.cv_pos))


class RefOrbViewWidget(BaseObject, SiriusDialog):
    """Matrix widget."""

    UM2M = 1e-6

    def __init__(self, parent, device, prefix=''):
        """Init."""
        BaseObject.__init__(self, device, prefix)
        SiriusDialog.__init__(self, parent)
        self.setObjectName('SIApp')
        self._setupui()
        self.refx = _ConnSig(self.devpref.substitute(propty='RefOrbX-RB'))
        self.refx.new_value_signal[_np.ndarray].connect(
            _part(self._update_implemented_ref, 'x'))
        self.refy = _ConnSig(self.devpref.substitute(propty='RefOrbY-RB'))
        self.refy.new_value_signal[_np.ndarray].connect(
            _part(self._update_implemented_ref, 'y'))
        ref = _np.zeros(self._csorb.nr_bpms, dtype=float)
        self.update_new_value_curves(ref, ref)
        self._update_horizontal()

    def _setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel('Reference Orbit', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)

        for plane in ['x', 'y']:
            graph = Graph(self)
            name = 'graph_' + plane
            setattr(self, name, graph)
            graph.setTitle('Horizontal' if plane == 'x' else 'Vertical')
            graph.setObjectName(name)
            graph.setStyleSheet('#'+name+'{min-width: 16em; min-height: 8em;}')
            graph.setLabel('bottom', text='BPM Position', units='m')
            graph.setLabel('left', text=plane, units='m')
            color = 'blue' if plane == 'x' else 'red'
            opts = dict(
                y_channel='', x_channel='', name='Implemented',
                color=color, redraw_mode=2,
                lineStyle=1, lineWidth=2,
                symbol='o', symbolSize=10)
            graph.addChannel(**opts)
            color = QColor(0, 125, 255) if plane == 'x' \
                else QColor(255, 125, 0)
            opts = dict(
                y_channel='', x_channel='', name='New Value',
                color=color, redraw_mode=2,
                lineStyle=1, lineWidth=2,
                symbol='o', symbolSize=10)
            graph.addChannel(**opts)
            graph.plotItem.scene().sigMouseMoved.connect(
                _part(self._show_tooltip, plane))
            vbl.addWidget(graph)

    def _show_tooltip(self, plane, pos):
        graph = getattr(self, 'graph_' + plane)
        curve = graph.curveAtIndex(0)
        posx = curve.scatter.mapFromScene(pos).x()
        ind = _np.argmin(_np.abs(_np.array(self._csorb.bpm_pos)-posx))
        txt = '{0:s}'.format(self._csorb.bpm_nicknames[ind])
        QToolTip.showText(
            graph.mapToGlobal(pos.toPoint()),
            txt, graph, graph.geometry(), 500)

    def _update_horizontal(self):
        bpm_pos = _np.array(self._csorb.bpm_pos)
        for graph in [self.graph_x, self.graph_y]:
            for idx in [0, 1]:
                curve = graph.curveAtIndex(idx)
                curve.receiveXWaveform(bpm_pos)

    def _update_implemented_ref(self, plane, *args):
        ref = getattr(self, 'ref' + plane)
        value = ref.value
        if value is None:
            return
        graph = getattr(self, 'graph_' + plane)
        curve = graph.curveAtIndex(0)
        curve.receiveYWaveform(self.UM2M*_np.array(value))

    def update_new_value_curves(self, refx, refy):
        """Update new value curves."""
        curve = self.graph_x.curveAtIndex(1)
        curve.receiveYWaveform(self.UM2M*_np.array(refx))
        curve = self.graph_y.curveAtIndex(1)
        curve.receiveYWaveform(self.UM2M*_np.array(refy))
