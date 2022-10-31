"""Graphics module."""

from functools import partial as _part
import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QToolTip, QWidget, QVBoxLayout, QLabel, \
    QHBoxLayout, QCheckBox, QGridLayout

from pyqtgraph import mkBrush, mkPen

from siriuspy.devices import StrengthConv

from ..widgets import SiriusConnectionSignal as _ConnSig, QDoubleSpinBoxPlus,\
    SiriusDialog, SiriusSpinbox, SiriusLabel
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
    """Corrector gain widget."""

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
    """RefOrb View widget."""

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
            graph.setStyleSheet(
                '#'+name+'{min-width: 45em; min-height: 15em;}')
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


class KickWidget(BaseObject, QWidget):
    """Corrector kicks widget."""

    def __init__(self, parent, device, prefix=''):
        """Init."""
        BaseObject.__init__(self, device, prefix)
        QWidget.__init__(self, parent)
        self.setObjectName('SIApp')
        self._setupui()
        self._psconv = {
            psn: StrengthConv(psn, 'Ref-Mon', auto_mon=True)
            for psn in self._csorb.ch_names + self._csorb.cv_names}
        self.kickh = _ConnSig(self.devpref.substitute(propty='KickCH-Mon'))
        self.kickh.new_value_signal[_np.ndarray].connect(
            _part(self._update_graph, 'kick', 'h'))
        self.kickv = _ConnSig(self.devpref.substitute(propty='KickCV-Mon'))
        self.kickv.new_value_signal[_np.ndarray].connect(
            _part(self._update_graph, 'kick', 'v'))
        self.limh = _ConnSig(self.devpref.substitute(propty='CHAccSatMax-RB'))
        self.limh.new_value_signal[float].connect(
            _part(self._update_graph, 'lim', 'h'))
        self.limv = _ConnSig(self.devpref.substitute(propty='CVAccSatMax-RB'))
        self.limv.new_value_signal[float].connect(
            _part(self._update_graph, 'lim', 'v'))
        self.enblh = _ConnSig(self.devpref.substitute(propty='CHEnblList-RB'))
        self.enblh.new_value_signal[_np.ndarray].connect(
            _part(self._update_graph, 'enbl', 'h'))
        self.enblv = _ConnSig(self.devpref.substitute(propty='CVEnblList-RB'))
        self.enblv.new_value_signal[_np.ndarray].connect(
            _part(self._update_graph, 'enbl', 'v'))
        self._update_horizontal()

    def _setupui(self):
        lay = QGridLayout(self)
        lab = QLabel(
            '<h4>Fast Corrector Kicks</h4>', self, alignment=Qt.AlignCenter)
        lay.addWidget(lab, 0, 0, 1, 2)

        ldbuff = QLabel('Buffer Size:', self)
        pvname = self.devpref.substitute(
            prefix=self.prefix, propty='KickBufferSize-SP')
        sbbuff = SiriusSpinbox(self, pvname)
        lbbuffmon = SiriusLabel(self, pvname.substitute(propty_suffix='Mon'))
        lbbuff = SiriusLabel(self, pvname.substitute(propty_suffix='RB'))
        laybuff = QHBoxLayout()
        laybuff.setContentsMargins(0, 0, 0, 0)
        laybuff.addWidget(ldbuff)
        laybuff.addWidget(sbbuff)
        laybuff.addWidget(lbbuffmon)
        laybuff.addWidget(QLabel('/'))
        laybuff.addWidget(lbbuff)
        lay.addLayout(laybuff, 1, 0, alignment=Qt.AlignLeft)

        cblim = QCheckBox('Show Kick Limits', self)
        cblim.setChecked(True)
        lay.addWidget(cblim, 1, 1, alignment=Qt.AlignRight)

        row = 2
        for plane in ['h', 'v']:
            graph = Graph(self)
            name = 'graph_' + plane
            setattr(self, name, graph)
            graph.setTitle('Horizontal' if plane == 'h' else 'Vertical')
            graph.setObjectName(name)
            graph.setStyleSheet(
                '#'+name+'{min-width: 45em; min-height: 15em;}')
            graph.setLabel('bottom', text='Position', units='m')
            graph.setLabel('left', text='Kick', units='rad')
            graph.showLegend = False
            graph.maxRedrawRate = 8  # [Hz]

            # kicks
            color = 'blue' if plane == 'h' else 'red'
            opts = dict(
                y_channel='', x_channel='', name='',
                color=color, redraw_mode=2,
                lineStyle=1, lineWidth=1,
                symbol='o', symbolSize=10)
            graph.addChannel(**opts)

            # limits
            opts = dict(
                y_channel='', x_channel='', name='',
                color='black', redraw_mode=2,
                lineStyle=2, lineWidth=1)
            graph.addChannel(**opts)
            maxkick = graph.curveAtIndex(1)
            graph.addChannel(**opts)
            minkick = graph.curveAtIndex(2)

            cblim.toggled.connect(maxkick.setVisible)
            cblim.toggled.connect(minkick.setVisible)

            graph.plotItem.scene().sigMouseMoved.connect(
                _part(self._show_tooltip, plane))
            lay.addWidget(graph, row, 0, 1, 2)
            row += 1

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

    def _update_graph(self, data, plane, value):
        if value is None:
            return
        graph = getattr(self, 'graph_' + plane)
        if data == 'kick':
            data = _np.asarray(value)*self.URAD2RAD
            curve = graph.curveAtIndex(0)
            curve.receiveYWaveform(data)
        elif data == 'enbl':
            data = _np.asarray(value)
            curve = graph.curveAtIndex(0)
            offcor = QColor('black')
            offbrs, offpen, offsz = mkBrush(offcor), mkPen(offcor), 10
            oncor = QColor('blue') if plane == 'h' else QColor('red')
            onbrs, onpen, onsize = mkBrush(oncor), mkPen(oncor), 10
            brss, pens, sizes = [], [], []
            for val in data:
                if val:
                    brss.append(onbrs)
                    pens.append(onpen)
                    sizes.append(onsize)
                else:
                    brss.append(offbrs)
                    pens.append(offpen)
                    sizes.append(offsz)
            curve.opts['symbolBrush'] = brss
            curve.opts['symbolPen'] = pens
            curve.opts['symbolSize'] = sizes
        else:
            psnames = self._csorb.ch_names if plane == 'h' \
                else self._csorb.cv_names
            maxlim = _np.array([
                self._psconv[psn].conv_current_2_strength(value)
                for psn in psnames])*self.URAD2RAD
            maxc = graph.curveAtIndex(1)
            maxc.receiveYWaveform(maxlim)
            minlim = _np.array([
                self._psconv[psn].conv_current_2_strength(-value)
                for psn in psnames])*self.URAD2RAD
            minc = graph.curveAtIndex(2)
            minc.receiveYWaveform(minlim)

    def _update_horizontal(self):
        for plane in ['h', 'v']:
            graph = getattr(self, 'graph_' + plane)
            data = self._csorb.ch_pos if plane == 'h' else self._csorb.cv_pos
            data = _np.array(data)
            for idx in range(3):
                curve = graph.curveAtIndex(idx)
                curve.receiveXWaveform(data)
