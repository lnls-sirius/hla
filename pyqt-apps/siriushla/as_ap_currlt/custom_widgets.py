"""Custom widgets module."""

from pyqtgraph import ViewBox

from pydm import utilities
from pydm.widgets.timeplot import PyDMTimePlot, TimePlotCurveItem


class MyGraph(PyDMTimePlot):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.vb2 = ViewBox()
        self.plotItem.scene().addItem(self.vb2)
        self.vb2.setXLink(self.plotItem)
        self.plotItem.getAxis('right').linkToView(self.vb2)
        self.plotItem.showAxis('right')
        self._updateViews()
        self.plotItem.vb.sigResized.connect(self._updateViews)
        self.updatesAsynchronously = True

    def addCurve(self, plot_item, axis='left', curve_color=None):
        if curve_color is None:
            curve_color = utilities.colors.default_colors[
                len(self._curves) % len(utilities.colors.default_colors)]
            plot_item.color_string = curve_color
        self._curves.append(plot_item)
        if axis == 'left':
            self.plotItem.addItem(plot_item)
        elif axis == 'right':
            self.vb2.addItem(plot_item)
        else:
            raise ValueError('Choose a valid axis!')
        self.redraw_timer.start()
        # Connect channels
        for chan in plot_item.channels():
            if chan:
                chan.connect()

    def addYChannel(self, y_channel=None, name=None, color=None,
                    lineStyle=None, lineWidth=None, symbol=None,
                    symbolSize=None, axis='left'):
        """Reimplement addYChannel."""
        plot_opts = dict()
        plot_opts['symbol'] = symbol
        if symbolSize is not None:
            plot_opts['symbolSize'] = symbolSize
        if lineStyle is not None:
            plot_opts['lineStyle'] = lineStyle
        if lineWidth is not None:
            plot_opts['lineWidth'] = lineWidth

        # Add curve
        new_curve = TimePlotCurveItem(
            y_channel,
            plot_by_timestamps=self._plot_by_timestamps,
            name=name, color=color,
            **plot_opts)
        new_curve.setUpdatesAsynchronously(self.updatesAsynchronously)
        new_curve.setBufferSize(self._bufferSize)

        self.update_timer.timeout.connect(new_curve.asyncUpdate)
        self.addCurve(new_curve, axis, curve_color=color)

        new_curve.data_changed.connect(self.set_needs_redraw)
        self.redraw_timer.start()

    def _updateViews(self):
        self.vb2.setGeometry(self.plotItem.vb.sceneBoundingRect())
        self.vb2.linkedViewChanged(self.plotItem.vb, self.vb2.XAxis)
