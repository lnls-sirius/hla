"""Main module of the Application Interface."""

import enum as _enum

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGroupBox, QGridLayout, QWidget, QLabel, QHBoxLayout
from pydm.widgets import PyDMWaveformPlot, PyDMTimePlot
import qtawesome as _qta

from .. import util as _util
from ..widgets import SiriusMainWindow
from ..widgets import SiriusSpinbox, PyDMStateButton, SiriusLedState, \
    SiriusLabel, SiriusLedAlert


class DEVICES(_enum.IntEnum):
    """."""
    SHB = (0, 'Sub-harmonic Buncher', 'BUN1')
    Kly1 = (1, 'Klystron 1', 'KLY1')
    Kly2 = (2, 'Klystron 2', 'KLY2')

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
            'mdi.waves', color=_util.get_appropriate_color('LI')))

        self._setupui()

    def _setupui(self):
        """."""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        lay1 = QGridLayout()
        wid.setLayout(lay1)

        for dev in DEVICES:
            grbox = QGroupBox(dev.label, wid)
            lay = QGridLayout()
            lay.setContentsMargins(0, 0, 0, 0)
            grbox.setLayout(lay)
            lay.addWidget(ControlBox(grbox, dev), 0, 0)
            ivsq = GraphIvsQ(wid, dev)
            amp = GraphAmpPha(wid, dev)
            pha = GraphAmpPha(wid, dev, prop='Phase')

            lay.addWidget(ivsq, 0, 1)
            lay.addWidget(amp, 0, 2)
            lay.addWidget(pha, 0, 3)
            lay.setColumnStretch(0, 1)
            lay.setColumnStretch(1, 1)
            lay.setColumnStretch(2, 1)
            lay.setColumnStretch(3, 1)

            lay1.addWidget(grbox, dev.value, 0)


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
        lay1.addWidget(labb, row, 1, alignment=Qt.AlignCenter)
        lay1.addWidget(labc, row, 2, alignment=Qt.AlignCenter)

        props = (
            ('State', 'STREAM'), ('Trigger', 'EXTERNAL_TRIGGER_ENABLE'),
            ('Integral', 'INTEGRAL_ENABLE'), ('Feedback', 'FB_MODE'))
        for name, prop in props:
            row += 1
            lab1 = QLabel(name, self)
            sppv = 'LA-RF:LLRF:' + self.dev.pvname + ':SET_' + prop
            rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_' + prop
            sp1 = PyDMStateButton(self, init_channel=sppv)
            rb1 = SiriusLedState(self, init_channel=rbpv)
            lay1.addWidget(lab1, row, 0)
            lay1.addWidget(sp1, row, 1)
            lay1.addWidget(rb1, row, 2)

        props = [('Amp [%]', 'AMP'), ('Phase [°]', 'PHASE')]
        if self.dev != DEVICES.SHB:
            props.append(('Refl. Pow. [MW]', 'REFL_POWER_LIMIT'))
        for name, prop in props:
            row += 1
            laba = QLabel(name, self)
            sppv = 'LA-RF:LLRF:' + self.dev.pvname + ':SET_' + prop
            rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_' + prop
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
        hlay = QHBoxLayout()
        if self.dev == DEVICES.SHB:
            labc = QLabel('Phase Diff [°]', self)
            rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_PHASE_DIFF'
            rbc = SiriusLabel(self, init_channel=rbpv)
            rbc.precisionFromPV = False
            rbc.precision = 2
            lay1.addWidget(labc, row, 0, 1, 2)
            lay1.addWidget(rbc, row, 2)
            row += 1
        else:
            rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_INTERLOCK'
            rb1 = SiriusLedAlert(self, init_channel=rbpv)
            hlay.addWidget(QLabel('Refl. Pow. Intlk'))
            hlay.addWidget(rb1)

        hlay.addStretch()
        rbpv = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_TRIGGER_STATUS'
        rb2 = SiriusLedAlert(self, init_channel=rbpv)
        rb2.setOnColor(rb2.LightGreen)
        rb2.setOffColor(rb2.Red)
        hlay.addWidget(QLabel('Trig. Stts'))
        hlay.addWidget(rb2)
        lay1.addLayout(hlay, row, 0, 1, 3)


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
        graph.setBackgroundColor(QColor(_util.get_appropriate_color('LI')))
        graph.setShowLegend(True)
        graph.setAutoRangeX(True)
        graph.setAutoRangeY(True)
        graph.setMinXRange(0.0)
        graph.setMaxXRange(1.0)
        graph.plotItem.showButtons()
        graph.setAxisColor(QColor(0, 0, 0))
        graph.setYLabels('Q')
        graph.setXLabels('I')
        axx = graph.plotItem.getAxis('right')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setWidth(0)
        axx = graph.plotItem.getAxis('top')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setHeight(0)

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


class GraphAmpPha(QWidget):
    """."""

    def __init__(self, parent=None, dev=None, prop='Amp'):
        """."""
        super().__init__(parent=parent)
        try:
            self.dev = DEVICES(dev)
        except ValueError:
            self.dev = DEVICES.Kly1
        self.prop = prop
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
        graph.setBackgroundColor(QColor(_util.get_appropriate_color('LI')))
        graph.plotItem.showButtons()
        axx = graph.plotItem.getAxis('right')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setWidth(0)
        axx = graph.plotItem.getAxis('top')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setHeight(0)
        graph.setAxisColor(QColor(0, 0, 0))
        if self.prop == 'Amp':
            graph.setLabel('left', 'Amplitude')
            chname = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_CH1_AMP'
        else:
            graph.setLabel('left', 'Phase')
            chname = 'LA-RF:LLRF:' + self.dev.pvname + ':GET_CH1_PHASE'
        graph.plotItem.setLabel('bottom', 'Time')

        opts = dict(
            y_channel=chname,
            color='black',
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addYChannel(**opts)
        lay1.addWidget(graph, 0, 0)
