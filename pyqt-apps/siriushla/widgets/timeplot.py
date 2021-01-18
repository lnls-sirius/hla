import numpy as _np
import time

from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QMenu

from pyqtgraph import ViewBox

from pydm import utilities
from pydm.widgets.timeplot import TimePlotCurveItem, PyDMTimePlot, \
    DEFAULT_X_MIN

from siriuspy.clientarch import ClientArchiver


class SiriusTimePlotItem(TimePlotCurveItem):
    """Reimplement to do not receive inf values."""

    def setBufferSize(self, value):
        """Reimplement."""
        if self._bufferSize == int(value):
            return
        self._bufferSize = max(int(value), 2)

        old_data_buffer = _np.copy(self.data_buffer)
        self.points_accumulated = old_data_buffer.shape[1]
        self._min_y_value = min(old_data_buffer[1])
        self._max_y_value = max(old_data_buffer[1])

        self.data_buffer = _np.zeros((2, self._bufferSize),
                                     order='f', dtype=float)
        for i in range(self.points_accumulated):
            self.data_buffer = _np.roll(self.data_buffer, -1)
            self.data_buffer[0, self._bufferSize-1] = old_data_buffer[0, i]
            self.data_buffer[1, self._bufferSize-1] = old_data_buffer[1, i]

    @Slot(float)
    @Slot(int)
    def receiveNewValue(self, new_value):
        if not _np.isinf(new_value):
            super().receiveNewValue(new_value)


class SiriusTimePlot(PyDMTimePlot):
    """Reimplementation of PyDMTimePlot."""

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self._min_time = time.time()

        self.vb2 = ViewBox()
        self.plotItem.scene().addItem(self.vb2)
        self.vb2.setXLink(self.plotItem)
        self.plotItem.getAxis('right').linkToView(self.vb2)
        self._updateViews()
        self.plotItem.vb.sigResized.connect(self._updateViews)

        self.carch = None

        self.plotItem.showButtons()

    def addCurve(self, plot_item, axis='left', curve_color=None):
        """Reimplement to use right axis."""
        if curve_color is None:
            curve_color = utilities.colors.default_colors[
                len(self._curves) % len(utilities.colors.default_colors)]
            plot_item.color_string = curve_color
        self._curves.append(plot_item)
        if axis == 'left':
            self.plotItem.addItem(plot_item)
        elif axis == 'right':
            if not self.plotItem.getAxis('right').isVisible():
                self.plotItem.showAxis('right')
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
        """Reimplement to use SiriusTimePlotItem and right axis."""
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
        self.addCurve(new_curve, axis, curve_color=color)

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

    def _updateViews(self):
        self.vb2.setGeometry(self.plotItem.vb.sceneBoundingRect())
        self.vb2.linkedViewChanged(self.plotItem.vb, self.vb2.XAxis)

    def _get_value_from_arch(self, pvname, t_init, t_end,
                             process_type, process_bin_intvl):
        """Get values from archiver."""
        if self.carch is None:
            self.carch = ClientArchiver()
        data = self.carch.getData(pvname, t_init, t_end,
                                  process_type, process_bin_intvl)
        if not data:
            return
        timestamp, value, _, _ = data
        return timestamp, value

    def fill_curve_with_archdata(self, curve, pvname, t_init, t_end,
                                 factor=None, process_type='',
                                 process_bin_intvl=None):
        """Fill curve with archiver data."""
        data = self._get_value_from_arch(pvname, t_init, t_end,
                                         process_type, process_bin_intvl)
        if not data:
            return
        datax, datay = data
        self.fill_curve_buffer(curve, datax, datay, factor)

    def fill_curve_buffer(self, curve, datax, datay, factor=None):
        """Fill curve buffer."""
        nrpts = len(datax)
        if not nrpts:
            return
        buff = _np.zeros((2, self.bufferSize), order='f', dtype=float)
        if nrpts > self.bufferSize:
            smpls2discard = nrpts - self.bufferSize
            datax = datax[smpls2discard:]
            datay = datay[smpls2discard:]
            nrpts = len(datax)
        firstsmpl2fill = self.bufferSize - nrpts
        buff[0, firstsmpl2fill:] = datax
        buff[1, firstsmpl2fill:] = datay
        if factor:
            buff[1, :] /= factor
        curve.data_buffer = buff
        curve.points_accumulated = nrpts
        curve._min_y_value = min(datay)
        curve._max_y_value = max(datay)
        curve.latest_value = datay[-1]

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
