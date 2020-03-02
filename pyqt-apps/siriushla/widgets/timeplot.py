import numpy as np
import time
from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QMenu
from pydm.widgets.timeplot import TimePlotCurveItem, PyDMTimePlot, \
    DEFAULT_X_MIN


class SiriusTimePlotItem(TimePlotCurveItem):
    """Reimplement to do not receive inf values."""

    @Slot(float)
    @Slot(int)
    def receiveNewValue(self, new_value):
        if not np.isinf(new_value):
            super().receiveNewValue(new_value)


class SiriusTimePlot(PyDMTimePlot):
    """Reimplement to use SiriusTimePlotItem."""

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self._min_time = time.time()

    def addYChannel(self, y_channel=None, name=None, color=None,
                    lineStyle=None, lineWidth=None, symbol=None,
                    symbolSize=None):
        """Reimplement to use SiriusTimePlotItem."""
        plot_opts = dict()
        plot_opts['symbol'] = symbol
        if symbolSize is not None:
            plot_opts['symbolSize'] = symbolSize
        if lineStyle is not None:
            plot_opts['lineStyle'] = lineStyle
        if lineWidth is not None:
            plot_opts['lineWidth'] = lineWidth

        # Add curve
        new_curve = SiriusTimePlotItem(
            y_channel,
            plot_by_timestamps=self._plot_by_timestamps,
            name=name, color=color, **plot_opts)
        new_curve.setUpdatesAsynchronously(self.updatesAsynchronously)
        new_curve.setBufferSize(self._bufferSize)

        self.update_timer.timeout.connect(new_curve.asyncUpdate)
        self.addCurve(new_curve, curve_color=color)

        new_curve.data_changed.connect(self.set_needs_redraw)
        self.redraw_timer.start()

        return new_curve

    def updateXAxis(self, update_immediately=False):
        """Reimplement to show only existing range."""
        if len(self._curves) == 0:
            return

        if self._plot_by_timestamps:
            if self._update_mode == PyDMTimePlot.SynchronousMode:
                maxrange = max([curve.max_x() for curve in self._curves])
            else:
                maxrange = time.time()

            mini = self._min_time
            for curve in self._curves:
                mini = min(mini, curve.data_buffer[0, 0])
            minrange = max(maxrange - self._time_span, mini)

            self.plotItem.setXRange(
                minrange, maxrange, padding=0.0, update=update_immediately)
        else:
            diff_time = self.starting_epoch_time - \
                max([curve.max_x() for curve in self._curves])
            if diff_time > DEFAULT_X_MIN:
                diff_time = DEFAULT_X_MIN
            self.getViewBox().setLimits(minXRange=diff_time)

    def mouseReleaseEvent(self, ev):
        """Reimplement context menu."""
        if ev.button() == Qt.RightButton:
            menu = QMenu(self)
            pi = self.plotItem
            vb = pi.getViewBox()
            sc = vb.scene()
            for act in vb.menu.actions():
                menu.addAction(act)
            menu.addSeparator()
            menu.addMenu(pi.ctrlMenu)
            menu.addAction(sc.contextMenu[0])
            menu.addSeparator()
            rst_act = menu.addAction("Clear buffers")
            rst_act.triggered.connect(self._resetBuffers)
            menu.exec_(self.mapToGlobal(ev.pos()))
        else:
            super().mouseReleaseEvent(ev)

    def _resetBuffers(self):
        for curve in self._curves:
            curve.initialize_buffer()
            self._min_time = time.time()
