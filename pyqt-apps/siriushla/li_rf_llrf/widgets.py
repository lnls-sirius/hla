"""LILLRF Custom Widgets."""

import numpy as np

from qtpy.QtGui import QColor
from qtpy.QtCore import QSize

from qtpy.QtWidgets import QPushButton, QGridLayout, \
    QWidget
from pydm.widgets import PyDMWaveformPlot
import qtawesome as _qta

from .. import util as _util
from ..widgets import SiriusTimePlot, SiriusConnectionSignal as _ConnSignal


class DeltaIQPhaseCorrButton(QPushButton):

    def __init__(self, parent=None, device=None, prefix='', delta=0,
                 show_label=True):
        label = str(abs(delta))+'°' if show_label else ''
        icon_name = 'mdi.plus' if np.sign(delta) == 1 else 'mdi.minus'
        icon = _qta.icon(icon_name)
        super().__init__(icon, label, parent)
        self.setIconSize(QSize(20, 20))

        self.prefix = prefix
        self.dev = device
        self.devpref = self.prefix + ('-' if self.prefix else '') + \
            'LA-RF:LLRF:' + self.dev.pvname
        self.delta = delta

        self.setToolTip(f'Do {delta:.1f}° delta')
        self.setEnabled(False)
        self.ch_loop_enable = _ConnSignal(
            self.devpref+':SET_FB_MODE')
        self.ch_loop_enable.new_value_signal[int].connect(
            self._handle_enable_state)
        self.ch_loop_enable.connection_state_signal.connect(
            self._handle_enable_state)

        self.ch_iqcorr_phase_ch1 = _ConnSignal(
            self.devpref+':SET_CH1_PHASE_CORR')

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
    """."""

    def __init__(self, parent=None, dev=None, prefix=''):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix
        self.dev = dev
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
        graph.setAutoRangeX(False)
        graph.setAutoRangeY(False)
        graph.setMinXRange(-1.0)
        graph.setMaxXRange(1.0)
        graph.setMinYRange(-1.0)
        graph.setMaxYRange(1.0)
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

        lay1.addWidget(graph, 0, 0)


class GraphAmpPha(QWidget):
    """."""

    def __init__(self, parent=None, dev=None, prop='Amp', prefix=''):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix
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
        graph.plotItem.setLabel('bottom', 'Time')
        graph.setTimeSpan(360)
        graph.setUpdateInterval(1/3)
        if self.prop == 'Amp':
            graph.setLabel('left', 'Amplitude')
            chname = basename + ':GET_CH1_AMP'
        else:
            graph.setLabel('left', 'Phase')
            chname = basename + ':GET_CH1_PHASE'

        opts = dict(
            y_channel=chname,
            color='black',
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addYChannel(**opts)
        lay1.addWidget(graph, 0, 0)


class RelativeWidget(QWidget):
    ''' Widget that stays in a relative position in the window '''
    ''' Relative position and size are given in percentage based on the parent size'''

    def __init__(self, parent=None, lay=None, relativePos=None):
        """."""
        super().__init__(parent=parent)
        self.parent = parent
        self.setLayout(lay)
        self.x = relativePos[0]
        self.y = relativePos[1]
        self.width = relativePos[2]
        self.height = relativePos[3]

    def relativeResize(self, event):
        ''' Resize and position in according to the relative position '''
        self.move(
            self.parent.geometry().width()*self.x/100,
            self.parent.geometry().height()*self.y/100)
        self.resize(
            self.parent.geometry().width()*self.width/100,
            self.parent.geometry().height()*self.height/100)
