"""Main module of the Application Interface."""

import enum as _enum

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGroupBox, QGridLayout, QWidget, QLabel, \
    QHBoxLayout, QPushButton
import qtawesome as _qta

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from .. import util as _util
from ..widgets import SiriusMainWindow, SiriusSpinbox, PyDMStateButton, \
    SiriusLedState, SiriusLabel, SiriusLedAlert, SiriusTimePlot, \
    SiriusWaveformPlot
from .details import DeviceParamSettingWindow
from .widgets import DeltaIQPhaseCorrButton


class DEVICES(_enum.IntEnum):
    """."""

    SHB = (0, 'Sub-harmonic Buncher', 'BUN1', 'SHB')
    Kly1 = (1, 'Klystron 1', 'KLY1', 'K1')
    Kly2 = (2, 'Klystron 2', 'KLY2', 'K2')

    def __new__(cls, value, label, pvname, nickname):
        """."""
        self = int.__new__(cls, value)
        self._value_ = value
        self.label = label
        self.pvname = pvname
        self.nickname = nickname
        return self


class MainWindow(SiriusMainWindow):
    """."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix
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
            lay.addWidget(ControlBox(grbox, dev, prefix=self.prefix), 0, 0)
            ivsq = GraphIvsQ(wid, dev, prefix=self.prefix)
            amp = GraphAmpPha(wid, dev, prefix=self.prefix)
            pha = GraphAmpPha(wid, dev, prop='Phase', prefix=self.prefix)

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

    def __init__(self, parent=None, dev=None, prefix=''):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix
        if dev not in DEVICES:
            dev = DEVICES.Kly1
        self.dev = dev
        self._setupui()

    def _setupui(self):
        """."""
        basename = self.prefix + ('-' if self.prefix else '') + \
            'LA-RF:LLRF:' + self.dev.pvname

        lay1 = QGridLayout()
        self.setLayout(lay1)

        row = 0
        labb = QLabel('Setpoint', self)
        labc = QLabel('Readback', self)
        lay1.addWidget(labb, row, 1, alignment=Qt.AlignCenter)
        lay1.addWidget(labc, row, 2, alignment=Qt.AlignCenter)

        pb_param = QPushButton(_qta.icon('fa5s.ellipsis-h'), '', self)
        pb_param.setToolTip('Open Parameter Setting Window')
        pb_param.setObjectName('detail')
        pb_param.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        _util.connect_window(
            pb_param, DeviceParamSettingWindow, parent=self,
            device=self.dev, prefix=self.prefix)
        lay1.addWidget(pb_param, row, 0, alignment=Qt.AlignLeft)

        props = (
            ('State', 'STREAM'), ('Trigger', 'EXTERNAL_TRIGGER_ENABLE'),
            ('Integral', 'INTEGRAL_ENABLE'), ('Feedback', 'FB_MODE'))
        for name, prop in props:
            row += 1
            lab1 = QLabel(name, self)
            sppv = basename + ':SET_' + prop
            rbpv = basename + ':GET_' + prop
            sp1 = PyDMStateButton(self, init_channel=sppv)
            rb1 = SiriusLedState(self, init_channel=rbpv)
            lay1.addWidget(lab1, row, 0)
            lay1.addWidget(sp1, row, 1)
            lay1.addWidget(rb1, row, 2)

        props = [('Amp [%]', 'AMP'), ('Phase [°]', 'PHASE'),
                 ('↳ ΔPhase (IQ Corr)', '')]
        if self.dev != DEVICES.SHB:
            props.append(('Refl. Pow. [MW]', 'REFL_POWER_LIMIT'))
        for name, prop in props:
            row += 1
            laba = QLabel(name, self)
            if 'IQ Corr' in name:
                dniqc = DeltaIQPhaseCorrButton(
                    self, self.dev, prefix=self.prefix, delta=-90)
                dpiqc = DeltaIQPhaseCorrButton(
                    self, self.dev, prefix=self.prefix, delta=90)
                lay1.addWidget(laba, row, 0)
                lay1.addWidget(dniqc, row, 1, alignment=Qt.AlignCenter)
                lay1.addWidget(dpiqc, row, 2, alignment=Qt.AlignCenter)
            else:
                sppv = basename + ':SET_' + prop
                rbpv = basename + ':GET_' + prop
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
            rbpv = basename + ':GET_PHASE_DIFF'
            rbc = SiriusLabel(self, init_channel=rbpv)
            rbc.precisionFromPV = False
            rbc.precision = 2
            lay1.addWidget(labc, row, 0, 1, 2)
            lay1.addWidget(rbc, row, 2)
            row += 1
        else:
            rbpv = basename + ':GET_INTERLOCK'
            rb1 = SiriusLedAlert(self, init_channel=rbpv)
            hlay.addWidget(QLabel('Refl. Pow. Intlk'))
            hlay.addWidget(rb1)

        hlay.addStretch()
        rbpv = basename + ':GET_TRIGGER_STATUS'
        rb2 = SiriusLedAlert(self, init_channel=rbpv)
        rb2.setOnColor(rb2.LightGreen)
        rb2.setOffColor(rb2.Red)
        hlay.addWidget(QLabel('Trig. Stts'))
        hlay.addWidget(rb2)
        lay1.addLayout(hlay, row, 0, 1, 3)

        self.setStyleSheet(
            "DeltaIQPhaseCorrButton{max-width: 3em;}")


class GraphIvsQ(QWidget):
    """."""

    def __init__(self, parent=None, dev=None, prefix=''):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix
        if dev not in DEVICES:
            dev = DEVICES.Kly1
        self.dev = dev
        self._setupui()

    def _setupui(self):
        """."""
        lay1 = QGridLayout()
        self.setLayout(lay1)

        graph = SiriusWaveformPlot(self)
        graph.setObjectName('graph')
        graph.setStyleSheet('#graph {min-height: 15em; min-width: 20em;}')
        graph.maxRedrawRate = 2
        graph.mouseEnabledX = True
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(_util.get_appropriate_color('LI')))
        graph.setShowLegend(True)
        graph.setAutoRangeX(False)
        graph.setAutoRangeY(False)
        graph.setMinXRange(-1.0)
        graph.setMaxXRange(1.0)
        graph.setMinYRange(-1.0)
        graph.setMaxYRange(1.0)
        graph.setAxisColor(QColor(0, 0, 0))
        axx = graph.plotItem.getAxis('right')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setWidth(0)
        axx = graph.plotItem.getAxis('top')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setHeight(0)

        basename = self.prefix + ('-' if self.prefix else '') + \
            'LA-RF:LLRF:' + self.dev.pvname
        opts = dict(
            y_channel=basename + ':GET_CH1_Q',
            x_channel=basename + ':GET_CH1_I',
            name='Data',
            color='red',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        opts = dict(
            y_channel=basename + ':GET_CH1_SETTING_Q',
            x_channel=basename + ':GET_CH1_SETTING_I',
            name='Setpoint',
            color='blue',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)

        graph.setLabel('left', text='Q', color='k')
        graph.setLabel('bottom', text='I', color='k')

        lay1.addWidget(graph, 0, 0)


class GraphAmpPha(QWidget):
    """."""

    def __init__(self, parent=None, dev=None, prop='Amp', prefix=''):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix
        if dev not in DEVICES:
            dev = DEVICES.Kly1
        self.dev = dev
        self.prop = prop
        self._setupui()

    def _setupui(self):
        """."""
        basename = self.prefix + ('-' if self.prefix else '') + \
            'LA-RF:LLRF:' + self.dev.pvname
        lay1 = QGridLayout()
        self.setLayout(lay1)

        graph = SiriusTimePlot(self)
        graph.setObjectName('graph')
        graph.setStyleSheet('#graph {min-height: 7em; min-width: 20em;}')
        graph.maxRedrawRate = 2
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(_util.get_appropriate_color('LI')))
        axx = graph.plotItem.getAxis('right')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setWidth(0)
        axx = graph.plotItem.getAxis('top')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setHeight(0)
        graph.setAxisColor(QColor(0, 0, 0))
        graph.setTimeSpan(360)
        graph.setUpdateInterval(1/3)
        if self.prop == 'Amp':
            ylabel = 'Amplitude'
            chname = basename + ':GET_CH1_AMP'
        else:
            ylabel = 'Phase'
            chname = basename + ':GET_CH1_PHASE'

        opts = dict(
            y_channel=chname,
            color='black',
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addYChannel(**opts)

        graph.setLabel('left', ylabel, color='k')
        graph.setLabel('bottom', 'Time', color='k')

        lay1.addWidget(graph, 0, 0)
