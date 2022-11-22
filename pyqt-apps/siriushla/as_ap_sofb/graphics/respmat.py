"""Control the Orbit Graphic Display."""
from functools import partial as _part

import numpy as _np
from pyqtgraph import mkPen
# from pyqtgraph import functions
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, \
    QToolTip
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.sofb.csdev import SOFBFactory
from siriushla.widgets import SiriusConnectionSignal as _ConnSig, QSpinBoxPlus
from .base import Graph, InfLine


class ShowMatrixWidget(QWidget):

    def __init__(self, parent, device, acc, prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self.acc = acc.upper()
        self.setObjectName(self.acc+'App')
        self._csorb = SOFBFactory.create(acc)
        self._inflines = []
        self.setupui()
        self.mat = _ConnSig(self.devpref.substitute(propty='RespMat-Mon'))
        self.mat.new_value_signal[_np.ndarray].connect(self._update_graph)
        self.rsize = _ConnSig(self.devpref.substitute(propty='RingSize-RB'))
        self.rsize.new_value_signal[int].connect(self._update_horizontal)
        self._update_horizontal(None)
        self._update_graph(None)

    def setupui(self):
        vbl = QVBoxLayout(self)

        lab = QLabel('Response Matrix', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)

        graph = Graph(self)
        vbl.addWidget(graph)

        self.spbox = QSpinBoxPlus(self)
        self.spbox.setMaximum(1000)
        self.spbox.setValue(80)
        self.spbox.setKeyboardTracking(False)
        self.spbox.editingFinished.connect(self._update_graph)

        hbl = QHBoxLayout()
        vbl.addLayout(hbl)
        hbl.addWidget(QLabel('Lines spacing:', self))
        hbl.addWidget(self.spbox)
        hbl.addStretch()

        graph.setShowLegend(False)
        graph.setLabel('bottom', text='BPM Position', units='m')
        graph.setLabel('left', text='Matrix', units='m/rad')
        for i in range(self._csorb.nr_corrs):
            color = 'blue'
            if i >= self._csorb.nr_ch:
                color = 'red'
            if i >= self._csorb.nr_ch+self._csorb.nr_cv:
                color = 'black'
            opts = dict(
                y_channel='',
                x_channel='',  # self.devpref.substitute(propty='BPMPosS-Mon'),
                name='',
                color=color,
                redraw_mode=2,
                lineStyle=1,
                lineWidth=3,
                symbol='o',
                symbolSize=10)
            graph.addChannel(**opts)
        graph.plotItem.scene().sigMouseMoved.connect(self._show_tooltip)
        self.graph = graph

    def _show_tooltip(self, pos):
        names = self._csorb.bpm_nicknames
        cname = self._csorb.ch_nicknames + self._csorb.cv_nicknames
        if self._csorb.isring:
            cname += ['RF', ]
        posi = self._csorb.bpm_pos

        graph = self.graph
        curve = graph.curveAtIndex(0)
        posx = curve.scatter.mapFromScene(pos).x()
        if self._csorb.isring:
            posx = posx % self._csorb.circum
        ind = _np.argmin(_np.abs(_np.array(posi)-posx))
        posy = curve.scatter.mapFromScene(pos).y()

        indy = int(posy // self.spbox.value())
        indy = max(min(indy, len(cname)-1), 0)
        # sca, prf = functions.siScale(posy)
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

    def _update_horizontal(self, _):
        val = self.rsize.getvalue()
        if val is None:
            val = 1
        bpm_pos = _np.array(self._csorb.bpm_pos)
        bpm_pos = [bpm_pos + i*self._csorb.circum for i in range(2*val)]
        bpm_pos = _np.hstack(bpm_pos)
        for i in range(self._csorb.nr_corrs):
            cur = self.graph.curveAtIndex(i)
            cur.receiveXWaveform(bpm_pos)

        for cur in self._inflines:
            self.graph.removeItem(cur)
        self._inflines = []
        for i in range(2*val+1):
            dic = {'style': 2, 'width': 2, 'color': '000'}
            if i == val:
                dic = {'style': 1, 'width': 3, 'color': '000'}
            pen = mkPen(**dic)
            line = InfLine(pos=i*self._csorb.circum+bpm_pos[0]/2, pen=pen)
            self._inflines.append(line)
            self.graph.addItem(line)


class SingularValues(QWidget):

    def __init__(self, parent, device, prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self.setObjectName(self.device.sec+'App')
        self._chan = _ConnSig(
            self.devpref.substitute(propty='NrSingValues-Mon'))
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        vbl.setAlignment(Qt.AlignCenter)
        lab = QLabel('Singular Values', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)
        graph = Graph()
        graph.setShowLegend(False)
        graph.plotItem.setLogMode(y=True)
        graph.setLabel('left', text='Singular Values', units='m/rad')
        graph.setLabel('bottom', text='Index')
        graph.setShowLegend(True)
        vbl.addWidget(graph)
        opts = dict(
            name='Processed',
            y_channel=self.devpref.substitute(propty='SingValues-Mon'),
            color='black',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=2,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        cur = graph.curveAtIndex(0)
        cur.setSymbolBrush(0, 0, 0)

        opts = dict(
            name='Raw',
            y_channel=self.devpref.substitute(propty='SingValuesRaw-Mon'),
            color='blue',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=2,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)

        pen = mkPen(QColor(150, 150, 150))
        pen.setStyle(2)
        pen.setWidth(3)
        line = InfLine(pos=0, pen=pen, angle=90)
        graph.addItem(line)
        self._chan.new_value_signal[int].connect(_part(self.setValue, line))

        graph.setObjectName('graph_singvalues')
        graph.setStyleSheet(
            "#graph_singvalues{min-width:30em; min-height:22m;}")

    def setValue(self, line, value):
        line.setValue(value-0.8)
