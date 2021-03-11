
from functools import partial as _part
import numpy as _np

from qtpy.QtCore import Signal, Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QGridLayout

from pydm.widgets import PyDMWaveformPlot

from siriuspy.search import PSSearch
from siriushla.widgets import SiriusConnectionSignal, SiriusMainWindow, \
    QSpinBoxPlus, QDoubleSpinBoxPlus


class Graph(PyDMWaveformPlot):
    doubleclick = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName('graph')
        self.setStyleSheet('#graph {min-height: 15em; min-width: 25em;}')
        self.maxRedrawRate = 2
        self.mouseEnabledX = True
        self.setShowXGrid(True)
        self.setShowYGrid(True)
        self.setBackgroundColor(QColor(255, 255, 255))
        self.setShowLegend(True)
        self.setAutoRangeX(True)
        self.setAutoRangeY(True)
        self.setMinXRange(0.0)
        self.setMaxXRange(1.0)
        self.plotItem.showButtons()
        self.setAxisColor(QColor(0, 0, 0))
        self.plotItem.getAxis('bottom').setStyle(tickTextOffset=15)
        self.plotItem.getAxis('left').setStyle(tickTextOffset=5)

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            posx = self.curveAtIndex(0).xData
            vb = self.plotItem.getViewBox()
            pos = vb.mapSceneToView(ev.pos())
            i = _np.argmin(_np.abs(posx-pos.x()))
            self.doubleclick.emit(i)
        super().mouseDoubleClickEvent(ev)


class GraphWidget(QWidget):

    def __init__(self, parent=None, pslist=[], name='', delta=0.0, idxini=0,
                 idxfin=4000, legend=False):
        super().__init__(parent)
        self._pvslist = pslist
        self.name = name
        self._legend = legend
        self._idx_ini = idxini
        self._idx_fin = idxfin
        self._delta = delta
        self.curves = []
        self.setupui()
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.chans = [SiriusConnectionSignal(ps+':Wfm-Mon') for ps in pslist]
        for idx, chan in enumerate(self.chans):
            chan.new_value_signal[_np.ndarray].connect(
                _part(self._update_curve, idx))

    def setupui(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(
            QLabel('<h2>'+self.name+'</h2>'), alignment=Qt.AlignCenter)
        self.graph = Graph(self)
        self.graph.setShowLegend(self._legend)
        self.graph.maxRedrawRate = 1/2
        self.layout().addWidget(self.graph)
        for i, pvn in enumerate(self._pvslist):
            frac = int(i / (len(self._pvslist)-1) * 255)
            color = QColor(frac, 0, 255-frac)
            opts = dict(
                y_channel='A',
                name=pvn,
                color=color,
                redraw_mode=2,
                lineStyle=1,
                lineWidth=1,
                symbol=None,
                symbolSize=None)
            self.graph.addChannel(**opts)
            self.curves.append(self.graph.curveAtIndex(i))

        spinini = QSpinBoxPlus(self)
        spinini.setMinimum(0)
        spinini.setMaximum(4000)
        spinini.setValue(self._idx_ini)
        spinini.editingFinished.connect(self._update_idx_ini)

        spindlt = QDoubleSpinBoxPlus(self)
        spindlt.setMinimum(0)
        spindlt.setMaximum(4)
        spindlt.setValue(self._delta)
        spindlt.editingFinished.connect(self._update_delta)

        spinfin = QSpinBoxPlus(self)
        spinfin.setMinimum(0)
        spinfin.setMaximum(4000)
        spinfin.setValue(self._idx_fin)
        spinfin.editingFinished.connect(self._update_idx_fin)

        hl = QHBoxLayout()
        hl.addWidget(QLabel('Spacing:', self))
        hl.addWidget(spindlt)
        hl.addStretch()
        hl.addWidget(QLabel('Initial Index:', self))
        hl.addWidget(spinini)
        hl.addStretch()
        hl.addWidget(QLabel('Final Index:', self))
        hl.addWidget(spinfin)
        hl.addStretch()
        self.layout().addLayout(hl)

    def _update_curve(self, idx, value):
        if value is None:
            return
        value = _np.array(value[self._idx_ini:self._idx_fin])
        value += self._delta*idx
        xval = _np.arange(self._idx_ini, self._idx_fin)
        self.curves[idx].receiveYWaveform(value)
        self.curves[idx].receiveXWaveform(xval)

    def _update_idx_ini(self):
        self._idx_ini = self.sender().value()

    def _update_delta(self):
        self._delta = self.sender().value()

    def _update_idx_fin(self):
        self._idx_fin = self.sender().value()


class PlotWfmErrorWindow(SiriusMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('BOApp')
        self.setupui()

    def setupui(self):
        chs = PSSearch.get_psnames({'sec': 'BO', 'dev': 'CH'})
        cvs = PSSearch.get_psnames({'sec': 'BO', 'dev': 'CV'})
        quads = PSSearch.get_psnames({'sec': 'BO', 'dev': 'Q(F|D)'})
        sexts = PSSearch.get_psnames({'sec': 'BO', 'dev': 'S.*'})
        dips = PSSearch.get_psnames({'sec': 'BO', 'dev': 'B'})

        wid = QWidget(self)
        self.setCentralWidget(wid)
        chwid = GraphWidget(
            wid, chs, name='CHs', delta=0.05, idxini=25, idxfin=606,
            legend=False)
        cvwid = GraphWidget(
            wid, cvs, name='CVs', delta=0.05, idxini=25, idxfin=606,
            legend=False)
        dipwid = GraphWidget(
            wid, dips, name='Dipoles', delta=0.0, idxini=110, idxfin=2440,
            legend=True)
        quadwid = GraphWidget(
            wid, quads, name='Quadrupoles', delta=0.0, idxini=110,
            idxfin=2440, legend=True)
        sextwid = GraphWidget(
            wid, sexts, name='Sextupoles', delta=0.0, idxini=110, idxfin=2440,
            legend=True)

        wid.setLayout(QGridLayout())
        wid.layout().addWidget(chwid, 0, 0)
        wid.layout().addWidget(cvwid, 0, 1)
        wid.layout().addWidget(quadwid, 1, 0)
        wid.layout().addWidget(sextwid, 1, 1)
        wid.layout().addWidget(dipwid, 2, 0, 1, 2)
