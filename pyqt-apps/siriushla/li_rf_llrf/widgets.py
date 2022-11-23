"""LI LLRF Custom Widgets."""

import numpy as np

from qtpy.QtGui import QColor
from qtpy.QtCore import Qt, QSize

from qtpy.QtWidgets import QPushButton, QGridLayout, \
    QWidget, QHBoxLayout
import qtawesome as _qta
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from .. import util as _util
from ..widgets import SiriusTimePlot, SiriusWaveformPlot, \
    SiriusConnectionSignal as _ConnSignal


class DeltaIQPhaseCorrButton(QPushButton):
    """."""
    def __init__(self, parent=None, device=None, main_dev='', delta=0,
                 show_label=True, prefix=''):
        """."""
        label = str(abs(delta)) + '°' if show_label else ''
        icon_name = 'mdi.plus' if np.sign(delta) == 1 else 'mdi.minus'
        icon = _qta.icon(icon_name)
        super().__init__(icon, label, parent)
        self.setIconSize(QSize(20, 20))

        self.prefix = prefix
        self.main_dev = main_dev
        self.dev = device
        self.devpref = self.prefix + self.main_dev + device
        self.delta = delta

        self.setToolTip(f'Do {delta:.1f}° delta')
        self.setEnabled(False)
        self.ch_loop_enable = _ConnSignal(
            self.devpref + ':SET_FB_MODE')
        self.ch_loop_enable.new_value_signal[int].connect(
            self._handle_enable_state)
        self.ch_loop_enable.connection_state_signal.connect(
            self._handle_enable_state)

        self.ch_iqcorr_phase_ch1 = _ConnSignal(
            self.devpref + ':SET_CH1_PHASE_CORR')

        self.clicked.connect(self._do_delta)

    def _do_delta(self):
        if not self.isEnabled():
            return
        if not self.ch_iqcorr_phase_ch1.connected:
            return
        curr_value = self.ch_iqcorr_phase_ch1.value
        new_value = curr_value + self.delta
        new_value = (new_value + 180) % 360 - 180
        self.ch_iqcorr_phase_ch1.send_value_signal[float].emit(new_value)

    def _handle_enable_state(self):
        state = (
            self.ch_loop_enable.connected and  # is connected
            self.ch_loop_enable.value == 0)    # is disabled
        self.setEnabled(state)


class GraphIvsQ(QWidget):
    """Show the I&Q Chart based on IxQ or Time"""

    def __init__(
        self, parent=None, dev=None,
        prop='Time', main_dev='', channel='CH1', prefix=''):
            """."""
            super().__init__(parent=parent)
            self.prefix = prefix
            self.main_dev = main_dev
            self.dev = dev
            self.prop = prop
            self.channel = channel
            self._setupui()

    def _setupui(self):
        """."""
        channels = {}
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
        graph.plotItem.showButtons()
        graph.setAxisColor(QColor(0, 0, 0))
        axx = graph.plotItem.getAxis('right')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setWidth(0)
        axx = graph.plotItem.getAxis('top')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setHeight(0)

        basename = self.prefix + self.main_dev + self.dev
        if self.prop == 'IvsQ':
            chart_title = "I & Q Fasor"
            lblAxis = ["Q", "I"]
            channels = {
                'Data': {
                    'X': basename + ':GET_' + self.channel + '_I',
                    'Y': basename + ':GET_' + self.channel + '_Q'
                },
                'Setpoint': {
                    'X': basename + ':GET_' + self.channel + '_SETTING_I',
                    'Y': basename + ':GET_' + self.channel + '_SETTING_Q'
                }
            }
            graph.setMinXRange(-1.0)
            graph.setMaxXRange(1.0)
            graph.setMinYRange(-1.0)
            graph.setMaxYRange(1.0)
        else:
            chart_title = "I & Q Waveform"
            lblAxis = ["I & Q", "Time"]
            channels = {
                'Data': {
                    'X': None,
                    'Y': basename + ':WF_ADC' + self.channel[2] + '_I'
                },
                'Setpoint': {
                    'X': None,
                    'Y': basename + ':WF_ADC' + self.channel[2] + '_Q'
                }
            }

        graph.setYLabels([lblAxis[0]])
        graph.setXLabels([lblAxis[1]])
        graph.setPlotTitle(chart_title)

        opts = dict(
            y_channel=channels['Data']['Y'],
            x_channel=channels['Data']['X'],
            name='Data',
            color='red',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)

        if ((self.prop != 'IvsQ') or (self.channel == 'CH1')):
            opts = dict(
                y_channel=channels['Setpoint']['Y'],
                x_channel=channels['Setpoint']['X'],
                name='Setpoint',
                color='blue',
                redraw_mode=2,
                lineStyle=1,
                lineWidth=3,
                symbol='o',
                symbolSize=10)
            graph.addChannel(**opts)

        lay1.addWidget(graph, 0, 0)


class GraphTime(QWidget):
    """Show the graphs of Amplitude, Phase,
    Pulse Amplitude, Pulse Phase, Diff and Raw Data"""

    def __init__(
        self, parent=None, dev='', prop='Amp', main_dev='', channel='CH1', prefix=''):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix
        self.main_dev = main_dev
        self.dev = dev
        self.prop = prop
        self.channel = channel
        self._setupui()

    def _setupui(self):
        """."""
        chart_name = self.prop
        basename = self.prefix + self.main_dev + self.dev
        lay1 = QGridLayout()
        self.setLayout(lay1)

        graph = SiriusTimePlot(self)
        graph.setObjectName('graph')
        graph.setStyleSheet('#graph {min-height: 15em; min-width: 20em;}')
        graph.maxRedrawRate = 2
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(_util.get_appropriate_color('LI')))
        graph.setShowLegend(True)
        graph.plotItem.showButtons()
        graph.setAxisColor(QColor(0, 0, 0))
        graph.setXLabels(["Time"])
        axx = graph.plotItem.getAxis('right')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setWidth(0)
        axx = graph.plotItem.getAxis('top')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setHeight(0)

        if self.prop == 'Amp':
            chart_name = 'Amplitude'
            chname = basename + ':GET_' + self.channel + '_AMP'
        elif self.prop == 'Pha':
            chart_name = 'Phase'
            chname = basename + ':GET_' + self.channel + '_PHASE'
        elif self.prop == 'PAmp':
            chart_name = 'Amplitude Waveform'
            chname = basename + ':WF_' + self.channel + 'AMP'
        elif self.prop == 'PPha':
            chart_name = 'Phase Waveform'
            chname = basename + ':WF_' + self.channel + 'PHASE'
        elif self.prop == 'Diff':
            chart_name = 'Phase Diff'
            chname = basename + ':GET_PHASE_DIFF'
        else:
            chart_name = 'Raw Data'
            chname = basename + ':WF_ADC9'

        graph.setPlotTitle(chart_name)
        graph.setYLabels([chart_name])

        opts = dict(
            y_channel=chname,
            name='Data',
            color='black',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addYChannel(**opts)
        lay1.addWidget(graph, 0, 0)
