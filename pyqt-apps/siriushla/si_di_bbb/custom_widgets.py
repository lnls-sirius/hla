"""Custom Widgets Module."""

from functools import partial as _part
import numpy as np

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QFrame, QLabel, QSizePolicy as QSzPlcy

from pydm.widgets import PyDMWaveformPlot
from pydm.widgets.base import PyDMWidget
from pydm.widgets.scale import QScale, PyDMScaleIndicator

from siriushla.widgets import SiriusTimePlot, SiriusConnectionSignal


class WfmGraph(PyDMWaveformPlot):
    """PyDMWaveformPlot rederivation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName('graph')
        self.setStyleSheet(
            '#graph {min-height: 6em; min-width: 15em;}')

        self.maxRedrawRate = 2

        self.autoRangeX = True
        self.autoRangeY = True
        self.minXRange = 0.0
        self.maxXRange = 1.0

        self.showXGrid = True
        self.showYGrid = True
        self.showLegend = False
        self.setAxisColor(QColor(0, 0, 0))
        self.backgroundColor = QColor(255, 255, 255)
        self.plotItem.showButtons()

        self._markers = dict()

    def add_scatter_curve(self, channel='', name='', color=QColor('blue'),
                          lineStyle=Qt.NoPen, lineWidth=1):
        self.addChannel(
            y_channel=channel, name=name, color=color,
            lineStyle=lineStyle, lineWidth=lineWidth,
            symbol='o', symbolSize=10)

    def add_marker(self, x_channel, y_channel, name,
                   color=QColor('blue'), symbol='o', symbolSize=10):
        self.addChannel(
            x_channel='FAKE:X', y_channel='FAKE:Y',
            name=name, color=color,
            lineStyle=Qt.NoPen, lineWidth=1,
            symbol=symbol, symbolSize=symbolSize)
        curve = self.curveAtIndex(-1)

        x_chan_obj = SiriusConnectionSignal(x_channel)
        x_chan_obj.new_value_signal[float].connect(
            _part(self._update_marker_value, curve, 'X'))
        y_chan_obj = SiriusConnectionSignal(y_channel)
        y_chan_obj.new_value_signal[float].connect(
            _part(self._update_marker_value, curve, 'Y'))
        self._markers[name] = [(x_chan_obj, y_chan_obj), curve]

    def _update_marker_value(self, curve, axis, value):
        func = getattr(curve, 'receive'+axis+'Waveform')
        func(np.array([value, ]))


class TimeGraph(SiriusTimePlot):
    """SiriusTimePlot rederivation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName('graph')
        self.setStyleSheet(
            '#graph {min-height: 6em; min-width: 8em;}')

        self.autoRangeX = True
        self.autoRangeY = True
        self.minXRange = 0.0
        self.maxXRange = 1.0

        self.showXGrid = True
        self.showYGrid = True
        self.showLegend = False
        self.setAxisColor(QColor(0, 0, 0))
        self.backgroundColor = QColor(255, 255, 255)


class MyScale(QScale):
    """QScale rederivation."""

    def calculate_position_for_value(self, value):
        """Rederivate calculate_position_for_value."""
        if value is None or value < self._lower_limit:
            proportion = -1  # Invalid
        elif value > self._upper_limit or\
                self._upper_limit - self._lower_limit == 0:
            proportion = 1  # Full
        else:
            proportion = (value - self._lower_limit) / \
                (self._upper_limit - self._lower_limit)

        position = int(proportion * self._widget_width)
        return position


class MyScaleIndicator(PyDMScaleIndicator):
    """PyDMScaleIndicator rederivation."""

    def __init__(self, parent=None, init_channel=None):
        QFrame.__init__(self, parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self._show_value = True
        self._show_limits = True

        self.scale_indicator = MyScale()
        self.value_label = QLabel()
        self.lower_label = QLabel()
        self.upper_label = QLabel()

        self.value_label.setText('<val>')
        self.lower_label.setText('<min>')
        self.upper_label.setText('<max>')

        self._value_position = Qt.TopEdge
        self._limits_from_channel = True
        self._user_lower_limit = 0
        self._user_upper_limit = 0

        self.value_label.setSizePolicy(
            QSzPlcy.Minimum, QSzPlcy.Minimum)
        self.setup_widgets_for_orientation(
            Qt.Horizontal, False, False, self._value_position)
