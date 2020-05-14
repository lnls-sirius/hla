"""Main module of the Application Interface."""

import enum as _enum

from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGroupBox, QGridLayout, QWidget, QLabel
from pydm.widgets import PyDMWaveformPlot, PyDMTimePlot
import qtawesome as _qta

from .. import util as _util
from ..widgets import SiriusMainWindow
from ..widgets import SiriusSpinbox, PyDMStateButton, SiriusLedState, \
    SiriusLabel


class DEVICES(_enum.IntEnum):
    """."""
    SHB = (0, 'Sub-harmonic Buncher', 'BUN1')
    Kly1 = (1, 'Klystron1', 'KLY1')
    Kly2 = (2, 'Klystron2', 'KLY2')

    def __new__(cls, value, label, pvname):
        """."""
        self = int.__new__(cls, value)
        self._value_ = value
        self.label = label
        self.pvname = pvname
        return self


class MainWindow(SiriusMainWindow):
    """."""

    def __init__(self, parent=None):
        """."""
        super().__init__(parent=parent)
        self.setObjectName('LIApp')
        self.setWindowTitle('LI LLRF')
        self.setWindowIcon(_qta.icon(
            'mdi.current-ac',
            color=_util.get_appropriate_color('LI')))

        self._setupui()

    def _setupui(self):
        """."""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        lay1 = QGridLayout()
        wid.setLayout(lay1)

        g_shb = QGroupBox('SHB', wid)
        lay_shb = QGridLayout()
        lay_shb.setContentsMargins(0,0,0,0)
        g_shb.setLayout(lay_shb)
        lay_shb.addWidget(ControlBox(g_shb, DEVICES.SHB), 0, 0)

        g_kly1 = QGroupBox('Kly1', wid)
        lay_kly1 = QGridLayout()
        lay_kly1.setContentsMargins(0,0,0,0)
        g_kly1.setLayout(lay_kly1)
        lay_kly1.addWidget(ControlBox(g_kly1, DEVICES.Kly1), 0, 0)

        g_kly2 = QGroupBox('Kly2', wid)
        lay_kly2 = QGridLayout()
        lay_kly2.setContentsMargins(0,0,0,0)
        g_kly2.setLayout(lay_kly2)
        lay_kly2.addWidget(ControlBox(g_kly2, DEVICES.Kly2), 0, 0)

        ivsq_shb = GraphIvsQ(wid, DEVICES.SHB)
        ivsq_kly1 = GraphIvsQ(wid, DEVICES.Kly1)
        ivsq_kly2 = GraphIvsQ(wid, DEVICES.Kly2)

        amp_shb = GraphAmp(wid, DEVICES.SHB)
        amp_kly1 = GraphAmp(wid, DEVICES.Kly1)
        amp_kly2 = GraphAmp(wid, DEVICES.Kly2)

        pha_shb = GraphPhase(wid, DEVICES.SHB)
        pha_kly1 = GraphPhase(wid, DEVICES.Kly1)
        pha_kly2 = GraphPhase(wid, DEVICES.Kly2)

        lay_shb.addWidget(ivsq_shb, 0, 1)
        lay_shb.addWidget(amp_shb, 0, 2)
        lay_shb.addWidget(pha_shb, 0, 3)

        lay_kly1.addWidget(ivsq_kly1, 0, 1)
        lay_kly1.addWidget(amp_kly1, 0, 2)
        lay_kly1.addWidget(pha_kly1, 0, 3)

        lay_kly2.addWidget(ivsq_kly2, 0, 1)
        lay_kly2.addWidget(amp_kly2, 0, 2)
        lay_kly2.addWidget(pha_kly2, 0, 3)

        lay1.addWidget(g_shb, 0, 0)
        lay1.addWidget(g_kly1, 1, 0)
        lay1.addWidget(g_kly2, 2, 0)


class ControlBox(QWidget):
    """."""

    def __init__(self, parent=None, dev=None):
        """."""
        super().__init__(parent=parent)
        try:
            self.dev = DEVICES(dev)
        except ValueError:
            self.dev = DEVICES.Kly1
        self._setupui()

    def _setupui(self):
        """."""
        lay1 = QGridLayout()
        self.setLayout(lay1)

        row = 0
        labb = QLabel('Setpoint', self)
        labc = QLabel('Readback', self)
        lay1.addWidget(labb, row, 1)
        lay1.addWidget(labc, row, 2)

        row += 1
        lab1 = QLabel('State', self)
        sppv = 'LA-RF:LLRF:' + self.dev.pvname + ':SET_STREAM'
        rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_STREAM'
        sp1 = PyDMStateButton(self, init_channel=sppv)
        rb1 = SiriusLedState(self, init_channel=rbpv)
        lay1.addWidget(lab1, row, 0)
        lay1.addWidget(sp1, row, 1)
        lay1.addWidget(rb1, row, 2)

        row += 1
        lab1 = QLabel('Trigger', self)
        sppv = 'LA-RF:LLRF:' + self.dev.pvname + ':SET_EXTERNAL_TRIGGER_ENABLE'
        rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_EXTERNAL_TRIGGER_ENABLE'
        sp1 = PyDMStateButton(self, init_channel=sppv)
        rb1 = SiriusLedState(self, init_channel=rbpv)
        lay1.addWidget(lab1, row, 0)
        lay1.addWidget(sp1, row, 1)
        lay1.addWidget(rb1, row, 2)

        row += 1
        lab1 = QLabel('Integral', self)
        sppv = 'LA-RF:LLRF:' + self.dev.pvname + ':SET_INTEGRAL_ENABLE'
        rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_INTEGRAL_ENABLE'
        sp1 = PyDMStateButton(self, init_channel=sppv)
        rb1 = SiriusLedState(self, init_channel=rbpv)
        lay1.addWidget(lab1, row, 0)
        lay1.addWidget(sp1, row, 1)
        lay1.addWidget(rb1, row, 2)

        row += 1
        lab1 = QLabel('Feedback', self)
        sppv = 'LA-RF:LLRF:' + self.dev.pvname + ':SET_FB_MODE'
        rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_FB_MODE'
        sp1 = PyDMStateButton(self, init_channel=sppv)
        rb1 = SiriusLedState(self, init_channel=rbpv)
        lay1.addWidget(lab1, row, 0)
        lay1.addWidget(sp1, row, 1)
        lay1.addWidget(rb1, row, 2)

        row += 1
        laba = QLabel('Amp [%]', self)
        sppv = 'LA-RF:LLRF:' + self.dev.pvname + ':SET_AMP'
        rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_AMP'
        spa = SiriusSpinbox(self, init_channel=sppv)
        spa.showStepExponent = False
        spa.precisionFromPV = False
        spa.precision = 2
        rba = SiriusLabel(self, init_channel=rbpv)
        rba.precisionFromPV = False
        rba.precision = 2
        lay1.addWidget(laba, row, 0)
        lay1.addWidget(spa, row, 1)
        lay1.addWidget(rba, row, 2)

        row += 1
        labb = QLabel('Phase [°]', self)
        sppv = 'LA-RF:LLRF:' + self.dev.pvname + ':SET_PHASE'
        rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_PHASE'
        spb = SiriusSpinbox(self, init_channel=sppv)
        spb.showStepExponent = False
        spb.precisionFromPV = False
        spb.precision = 2
        rbb = SiriusLabel(self, init_channel=rbpv)
        rbb.precisionFromPV = False
        rbb.precision = 2
        lay1.addWidget(labb, row, 0)
        lay1.addWidget(spb, row, 1)
        lay1.addWidget(rbb, row, 2)

        row += 1
        if not self.dev == DEVICES.SHB:
            labc = QLabel('Refl. Pow. [MW]', self)
            sppv = 'LA-RF:LLRF:' + self.dev.pvname + ':SET_REFL_POWER_LIMIT'
            rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_REFL_POWER_LIMIT'
            spc = SiriusSpinbox(self, init_channel=sppv)
            spc.showStepExponent = False
            spc.precisionFromPV = False
            spc.precision = 3
            rbc = SiriusLabel(self, init_channel=rbpv)
            rbc.precisionFromPV = False
            rbc.precision = 2
            lay1.addWidget(labc, row, 0)
            lay1.addWidget(spc, row, 1)
            lay1.addWidget(rbc, row, 2)
        else:
            labc = QLabel('Phase Diff [°]', self)
            rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_PHASE_DIFF'
            rbc = SiriusLabel(self, init_channel=rbpv)
            rbc.precisionFromPV = False
            rbc.precision = 2
            lay1.addWidget(labc, row, 0, 1, 2)
            lay1.addWidget(rbc, row, 2)


class GraphIvsQ(QWidget):
    """."""

    def __init__(self, parent=None, dev=None):
        """."""
        super().__init__(parent=parent)
        try:
            self.dev = DEVICES(dev)
        except ValueError:
            self.dev = DEVICES.Kly1
        self._setupui()

    def _setupui(self):
        """."""
        lay1 = QGridLayout()
        self.setLayout(lay1)

        graph = PyDMWaveformPlot(self)
        graph.setObjectName('graph')
        graph.setStyleSheet('#graph {min-height: 15em; min-width: 20em;}')
        graph.maxRedrawRate = 2
        graph.mouseEnabledX = True
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(255, 255, 255))
        graph.setShowLegend(True)
        graph.setAutoRangeX(True)
        graph.setAutoRangeY(True)
        graph.setMinXRange(0.0)
        graph.setMaxXRange(1.0)
        graph.plotItem.showButtons()
        graph.setAxisColor(QColor(0, 0, 0))
        graph.setYLabels('Q')
        graph.setXLabels('I')

        opts = dict(
            y_channel='LA-RF:LLRF:' + self.dev.pvname + ':GET_CH1_I',
            x_channel='LA-RF:LLRF:' + self.dev.pvname + ':GET_CH1_Q',
            name='Data',
            color='red',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        opts = dict(
            y_channel='LA-RF:LLRF:' + self.dev.pvname + ':GET_CH1_SETTING_I',
            x_channel='LA-RF:LLRF:' + self.dev.pvname + ':GET_CH1_SETTING_Q',
            name='Setpoint',
            color='blue',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)

        lay1.addWidget(graph, 0, 0)


class GraphAmp(QWidget):
    """."""

    def __init__(self, parent=None, dev=None):
        """."""
        super().__init__(parent=parent)
        try:
            self.dev = DEVICES(dev)
        except ValueError:
            self.dev = DEVICES.Kly1
        self._setupui()

    def _setupui(self):
        """."""
        lay1 = QGridLayout()
        self.setLayout(lay1)

        graph = PyDMTimePlot(self)
        graph.setObjectName('graph')
        graph.setStyleSheet('#graph {min-height: 7em; min-width: 20em;}')
        graph.maxRedrawRate = 2
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(255, 255, 255))
        graph.plotItem.showButtons()
        graph.setAxisColor(QColor(0, 0, 0))
        graph.setLabel('left', 'Amplitude')

        opts = dict(
            y_channel='LA-RF:LLRF:' + self.dev.pvname + ':GET_CH1_AMP',
            color='black',
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addYChannel(**opts)
        lay1.addWidget(graph, 0, 0)


class GraphPhase(QWidget):
    """."""

    def __init__(self, parent=None, dev=None):
        """."""
        super().__init__(parent=parent)
        try:
            self.dev = DEVICES(dev)
        except ValueError:
            self.dev = DEVICES.Kly1
        self._setupui()

    def _setupui(self):
        """."""
        lay1 = QGridLayout()
        self.setLayout(lay1)

        graph = PyDMTimePlot(self)
        graph.setObjectName('graph')
        graph.setStyleSheet('#graph {min-height: 7em; min-width: 20em;}')
        graph.maxRedrawRate = 2
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(255, 255, 255))
        graph.plotItem.showButtons()
        graph.setAxisColor(QColor(0, 0, 0))
        graph.setLabel('left', 'Phase')

        opts = dict(
            y_channel='LA-RF:LLRF:' + self.dev.pvname + ':GET_CH1_PHASE',
            color='black',
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addYChannel(**opts)
        lay1.addWidget(graph, 0, 0)
