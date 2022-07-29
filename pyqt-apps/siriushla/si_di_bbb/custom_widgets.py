"""Custom Widgets Module."""

from functools import partial as _part

import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QSizePolicy as QSzPlcy
from pyqtgraph import mkBrush
from pydm.widgets.scale import QScale, PyDMScaleIndicator

from ..widgets import SiriusTimePlot, SiriusConnectionSignal, \
    SiriusWaveformPlot


class WfmGraph(SiriusWaveformPlot):
    """SiriusWaveformPlot rederivation."""

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.setObjectName('graph')
        self.setStyleSheet(
            '#graph {min-height: 6em; min-width: 15em;}')

        self.addAxis(plot_data_item=None, name='left', orientation='left')

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

        self._markers = dict()
        self._curves_names = []

    def add_scatter_curve(
            self, ychannel='', xchannel='', name='', color=QColor('blue'),
            lineStyle=Qt.NoPen, lineWidth=1, symbolSize=10, nchannel=None,
            offset=None):
        """."""
        self.addChannel(
            x_channel='', y_channel='',
            name=name, color=color, lineStyle=lineStyle, lineWidth=lineWidth,
            symbol='o', symbolSize=symbolSize)
        curve = self.curveAtIndex(-1)
        curve.opts['symbolBrush'] = mkBrush(color)
        curve.nchannel = None
        curve.offset = offset
        if nchannel is not None:
            curve.nchannel = SiriusConnectionSignal(nchannel)
        x_chan_obj = SiriusConnectionSignal(xchannel)
        x_chan_obj.new_value_signal[np.ndarray].connect(
            _part(self._update_waveform_value, curve, 'X'))
        y_chan_obj = SiriusConnectionSignal(ychannel)
        y_chan_obj.new_value_signal[np.ndarray].connect(
            _part(self._update_waveform_value, curve, 'Y'))
        self._curves_names.append(((x_chan_obj, y_chan_obj), curve))

    def add_marker(
            self, xchannel, ychannel, name,
            color=QColor('blue'), symbol='o', symbolSize=10):
        """."""
        self.addChannel(
            x_channel='FAKE:X', y_channel='FAKE:Y',
            name=name, color=color,
            lineStyle=Qt.NoPen, lineWidth=1,
            symbol=symbol, symbolSize=symbolSize)
        curve = self.curveAtIndex(-1)
        curve.opts['symbolBrush'] = mkBrush(color)

        x_chan_obj = SiriusConnectionSignal(xchannel)
        x_chan_obj.new_value_signal[float].connect(
            _part(self._update_marker_value, curve, 'X'))
        y_chan_obj = SiriusConnectionSignal(ychannel)
        y_chan_obj.new_value_signal[float].connect(
            _part(self._update_marker_value, curve, 'Y'))
        self._markers[name] = [(x_chan_obj, y_chan_obj), curve]

    def _update_marker_value(self, curve, axis, value):
        func = getattr(curve, 'receive'+axis+'Waveform')
        func(np.array([value, ]))

    def _update_waveform_value(self, curve, axis, value):
        func = getattr(curve, 'receive'+axis+'Waveform')
        offset = curve.offset or 0.0
        value = value + offset
        if curve.nchannel is None:
            func(value)
            return
        npoints = curve.nchannel.value
        if npoints is None:
            func(value)
        else:
            func(value[:npoints])


class TimeGraph(SiriusTimePlot):
    """SiriusTimePlot rederivation."""

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.setObjectName('graph')
        self.setStyleSheet(
            '#graph {min-height: 6em; min-width: 8em;}')

        self.addAxis(plot_data_item=None, name='left', orientation='left')

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
        """."""
        super().__init__(parent, init_channel=init_channel)
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

        self.value_label.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Minimum)
        self.setup_widgets_for_orientation(
            Qt.Horizontal, False, False, self._value_position)
