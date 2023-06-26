"""Graphics module."""

from functools import partial as _part
import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QToolTip, QWidget, QVBoxLayout, QLabel, \
    QHBoxLayout, QCheckBox, QGridLayout

from pyqtgraph import mkBrush, mkPen

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.devices import StrengthConv
from siriuspy.optics.constants import SI as SICte

from ..widgets import SiriusConnectionSignal as _ConnSig, QDoubleSpinBoxPlus,\
    SiriusDialog
from ..as_ap_sofb.graphics.base import Graph, InfLine
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
        self._inflines = []
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
        self.spbox.setMinimum(0)
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

        sbval = self.spbox.value()
        if sbval == 0:
            indy = 0
        else:
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
        bpm_pos = [bpm_pos + i*SICte.length for i in range(2)]
        bpm_pos = _np.hstack(bpm_pos)
        ncorr = self._csorb.nr_chcv if self._is_coeff else self._csorb.nr_corrs
        for i in range(ncorr):
            cur = self.graph.curveAtIndex(i)
            pos = bpm_pos
            if self._is_inv or self._is_coeff:
                pos = _np.hstack([-1, bpm_pos])
            cur.receiveXWaveform(pos)

        for cur in self._inflines:
            self.graph.removeItem(cur)
        self._inflines = []
        for i in range(3):
            dic = {'style': 2, 'width': 2, 'color': '000'}
            if i == 1:
                dic = {'style': 1, 'width': 3, 'color': '000'}
            pen = mkPen(**dic)
            line = InfLine(pos=i*SICte.length+bpm_pos[0]/2, pen=pen)
            self._inflines.append(line)
            self.graph.addItem(line)


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
            graph.plotItem.scene().sigMouseMoved.connect(
                _part(self._show_tooltip, plane))
            graph.setShowLegend(False)
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
            curve = graph.curveAtIndex(0)
            curve.receiveXWaveform(bpm_pos)

    def _update_implemented_ref(self, plane, *args):
        ref = getattr(self, 'ref' + plane)
        value = ref.value
        if value is None:
            return
        graph = getattr(self, 'graph_' + plane)
        curve = graph.curveAtIndex(0)
        curve.receiveYWaveform(self.UM2M*_np.array(value))


class KickWidget(BaseObject, QWidget):
    """Corrector kicks widget."""

    def __init__(self, parent, device, prefix=''):
        """Init."""
        BaseObject.__init__(self, device, prefix)
        QWidget.__init__(self, parent)
        self.setObjectName('SIApp')
        self._setupui()
        self._psconv = {
            psn: StrengthConv(psn, 'Ref-Mon', auto_monitor_mon=True)
            for psn in self._csorb.ch_names + self._csorb.cv_names}

        for suffix in ['-Mon', 'Acc-Mon', 'Ref-Mon']:
            for plane in ['h', 'v']:
                propty = 'KickC' + plane.upper() + suffix
                ktype = 'kick' + suffix.strip('-Mon').lower()
                pvn = self.devpref.substitute(propty=propty)
                chn = _ConnSig(pvn)
                chn.new_value_signal[_np.ndarray].connect(
                    _part(self._update_graph, ktype, plane))
                setattr(self, ktype+plane, chn)

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

        self.energy = _ConnSig(_PVName('SI-Fam:PS-B1B2-1').substitute(
            prefix=self.prefix, propty='EnergyRef-Mon'))
        self.energy.new_value_signal[float].connect(
            _part(self._update_graph, 'energy', 'h'))
        self.energy.new_value_signal[float].connect(
            _part(self._update_graph, 'energy', 'v'))

        self._update_horizontal()

    def _setupui(self):
        lay = QGridLayout(self)
        lab = QLabel(
            '<h4>Fast Corrector Kicks</h4>', self, alignment=Qt.AlignCenter)
        lay.addWidget(lab, 0, 0, 1, 2)

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
            graph.maxRedrawRate = 8  # [Hz]

            # kicks
            opts = dict(
                y_channel='', x_channel='', redraw_mode=2,
                lineStyle=1, lineWidth=1, symbol='o', symbolSize=10)
            # Current-Mon
            opts['color'] = 'gray'
            opts['name'] = 'Mon'
            graph.addChannel(**opts)
            # CurrentRef-Mon
            opts['color'] = QColor(0, 125, 255) if plane == 'h' \
                else QColor(255, 125, 0)
            opts['name'] = 'Ref'
            graph.addChannel(**opts)
            # FOFBAcc-Mon
            opts['color'] = 'blue' if plane == 'h' else 'red'
            opts['name'] = 'Acc'
            graph.addChannel(**opts)

            # limits
            opts = dict(
                y_channel='', x_channel='',
                color='black', redraw_mode=2,
                lineStyle=2, lineWidth=1)
            opts['name'] = 'maxlim'
            graph.addChannel(**opts)
            graph.legend.removeItem('maxlim')
            maxkick = graph.curveAtIndex(3)
            opts['name'] = 'minlim'
            graph.addChannel(**opts)
            minkick = graph.curveAtIndex(4)
            graph.legend.removeItem('minlim')

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
        if data.startswith('kick'):
            value = _np.asarray(value)*self.URAD2RAD
            idx = 2 if data.endswith('acc') else \
                1 if data.endswith('ref') else 0
            curve = graph.curveAtIndex(idx)
            curve.receiveYWaveform(value)
        elif data == 'enbl':
            value = _np.asarray(value)
            offcor = QColor('black')
            offbrs, offpen, offsz = mkBrush(offcor), mkPen(offcor), 10
            for cidx in range(3):
                curve = graph.curveAtIndex(cidx)
                if curve.latest_y is None:
                    continue
                onrgb = (127, 127, 127) if cidx == 0 else \
                    (0, 125*(cidx == 1), 255) if plane == 'h' \
                    else (255, 125*(cidx == 1), 0)
                oncor = QColor(*onrgb)
                onbrs, onpen, onsize = mkBrush(oncor), mkPen(oncor), 10
                brss, pens, sizes = [], [], []
                for val in value:
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
                curve.redrawCurve()
        else:
            if data == 'energy':
                value = self.limh.value if plane == 'h' \
                    else self.limv.value
                if value is None:
                    return
            psnames = self._csorb.ch_names if plane == 'h' \
                else self._csorb.cv_names
            maxlim = [
                self._psconv[psn].conv_current_2_strength(value)
                for psn in psnames]
            if None in maxlim:
                return
            maxlim = _np.array(maxlim)*self.URAD2RAD
            maxc = graph.curveAtIndex(3)
            maxc.receiveYWaveform(maxlim)
            minlim = [
                self._psconv[psn].conv_current_2_strength(-value)
                for psn in psnames]
            if None in minlim:
                return
            minlim = _np.array(minlim)*self.URAD2RAD
            minc = graph.curveAtIndex(4)
            minc.receiveYWaveform(minlim)

    def _update_horizontal(self):
        for plane in ['h', 'v']:
            graph = getattr(self, 'graph_' + plane)
            data = self._csorb.ch_pos if plane == 'h' else self._csorb.cv_pos
            data = _np.array(data)
            for idx in range(5):
                curve = graph.curveAtIndex(idx)
                curve.receiveXWaveform(data)
