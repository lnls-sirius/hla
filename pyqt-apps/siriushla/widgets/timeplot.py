import numpy as _np
import time

from qtpy.QtCore import Qt, Signal, Slot, QTimer, Property
from qtpy.QtGui import QPalette
from qtpy.QtWidgets import QInputDialog, QLabel, QApplication, QAction

from pyqtgraph import ViewBox, mkBrush

from pydm import utilities
from pydm.widgets.timeplot import TimePlotCurveItem, PyDMTimePlot, \
    DEFAULT_X_MIN

from siriuspy.clientarch import ClientArchiver, Time


class SiriusTimePlotItem(TimePlotCurveItem):
    """Reimplement to do not receive inf values."""

    def __init__(self, parent, *args, **kwargs):
        """Init and create parent attribute."""
        super().__init__(*args, **kwargs)
        self.parent = parent

    def setBufferSize(self, value, initialize_buffer=False):
        """
        Reimplement setBufferSize to fill buffer with points accumulated.
        """
        if self._bufferSize == int(value):
            return
        self._bufferSize = max(int(value), 2)

        if initialize_buffer:
            self.initialize_buffer()
        else:
            old_data_buffer = _np.copy(self.data_buffer)
            self.points_accumulated = old_data_buffer.shape[1]
            self._min_y_value = min(old_data_buffer[1])
            self._max_y_value = max(old_data_buffer[1])

            self.data_buffer = _np.zeros(
                (2, self._bufferSize), order='f', dtype=float)
            for i in range(self.points_accumulated):
                self.data_buffer = _np.roll(self.data_buffer, -1)
                self.data_buffer[0, self._bufferSize-1] = old_data_buffer[0, i]
                self.data_buffer[1, self._bufferSize-1] = old_data_buffer[1, i]

    @Slot(float)
    @Slot(int)
    def receiveNewValue(self, new_value):
        """
        Rederive receiveNewValue to avoid infinit values.
        """
        if not _np.isinf(new_value):
            super().receiveNewValue(new_value)

    @Slot()
    def redrawCurve(self):
        """
        Rederive redrawCurve to use data only refered to timespan.
        """
        try:
            now = Time.now().timestamp()
            xmin = now - self.parent.timeSpan
            idcs = _np.where(self.data_buffer[0] >= xmin)[0]
            x = self.data_buffer[0, idcs].astype(_np.float)
            y = self.data_buffer[1, idcs].astype(_np.float)

            if not self._plot_by_timestamps:
                x -= now

            self.setData(y=y, x=x)
        except (ZeroDivisionError, OverflowError):
            # Solve an issue with pyqtgraph and initial downsampling
            pass

    def initialize_buffer(self):
        """
        Rederive initialize_buffer to avoid filling the entire buffer
        with plot-eligible data.
        """
        self.points_accumulated = 0

        # If you don't specify dtype=float, you don't have enough
        # resolution for the timestamp data.
        self.data_buffer = _np.zeros((2, self._bufferSize),
                                     order='f', dtype=float)

class SiriusTimePlot(PyDMTimePlot):
    """PyDMTimePlot with some extra features."""

    bufferReset = Signal()
    timeSpanChanged = Signal()

    def __init__(self, *args, show_tooltip=False, **kws):
        super().__init__(*args, **kws)
        self._filled_with_arch_data = dict()
        self._show_tooltip = show_tooltip

        self.vb2 = ViewBox()
        self.plotItem.scene().addItem(self.vb2)
        self.vb2.setXLink(self.plotItem)
        self.plotItem.getAxis('right').linkToView(self.vb2)
        self._updateViews()
        self.plotItem.vb.sigResized.connect(self._updateViews)

        self.carch = None

        # show auto adjust button
        self.plotItem.showButtons()

        # use pan mouse mode (3-button)
        self.plotItem.getViewBox().setMouseMode(ViewBox.PanMode)

        # connect sigMouseMoved
        self.plotItem.scene().sigMouseMoved.connect(self._handle_mouse_moved)

        # add new actions to menu
        rst_act = QAction("Clear buffers")
        rst_act.triggered.connect(self._resetBuffers)
        tsp_act = QAction("Change time span")
        tsp_act.triggered.connect(self._changeTimeSpan)
        self.plotItem.scene().contextMenu.extend([rst_act, tsp_act])

    @Property(bool)
    def showToolTip(self):
        """
        Whether to show or not tooltip with curve values.

        Returns
        -------
        use : bool
            Tooltip enable status in use
        """
        return self._show_tooltip

    @showToolTip.setter
    def showToolTip(self, new_show):
        """
        Whether to show or not tooltip with curve values.

        Parameters
        ----------
        new_show : bool
            The new tooltip enable status to use
        """
        self._show_tooltip = new_show

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

    def addYChannel(
            self, y_channel=None, name=None, color=None, lineStyle=None,
            lineWidth=None, symbol=None, symbolSize=None, axis='left'):
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
            self, y_channel,
            plot_by_timestamps=self._plot_by_timestamps,
            name=name, color=color, **plot_opts)
        new_curve.setUpdatesAsynchronously(self.updatesAsynchronously)
        new_curve.setBufferSize(self._bufferSize, initialize_buffer=True)

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

            mini = Time.now().timestamp()
            for curve in self._curves:
                firstvalid = (curve.data_buffer[0] != 0).argmax()
                if curve.data_buffer[0, firstvalid] == 0:
                    continue
                mini = min(mini, curve.data_buffer[0, firstvalid])
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

    def _get_value_from_arch(
            self, pvname, t_init, t_end, process_type, process_bin_intvl):
        """Get values from archiver."""
        if self.carch is None:
            self.carch = ClientArchiver()
        self.carch.timeout = 120
        data = self.carch.getData(
            pvname, t_init, t_end, process_type, process_bin_intvl)
        if not data:
            return
        return data['timestamp'], data['value']

    def fill_curve_with_archdata(
            self, curve, pvname, t_init, t_end, factor=None, process_type='',
            process_bin_intvl=None):
        """Fill curve with archiver data."""
        data = self._get_value_from_arch(
            pvname, t_init, t_end, process_type, process_bin_intvl)
        if not data:
            return
        datax, datay = data
        self.fill_curve_buffer(curve, datax, datay, factor)

        self._filled_with_arch_data[pvname] = dict(
            curve=curve, factor=factor, process_type=process_type,
            process_bin_intvl=process_bin_intvl)

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

    def _resetBuffers(self):
        for curve in self._curves:
            curve.initialize_buffer()
        self.bufferReset.emit()

    def _changeTimeSpan(self):
        new_time_span, ok = QInputDialog.getInt(
            self, 'Input', 'Set new time span value [s]: ')
        if not ok:
            return

        if new_time_span > self.timeSpan:
            t_end = Time.now()
            t_init = t_end - new_time_span
            for pvname, info in self._filled_with_arch_data.items():
                self.fill_curve_with_archdata(
                    info['curve'], pvname,
                    t_init.get_iso8601(), t_end.get_iso8601(),
                    info['factor'], info['process_type'],
                    info['process_bin_intvl'])

        self.timeSpan = new_time_span
        self.timeSpanChanged.emit()

    def _handle_mouse_moved(self, pos):
        """Show tooltip at mouse move."""
        if not self._show_tooltip:
            return

        # create label tooltip, if needed
        if not hasattr(self, 'label_tooltip'):
            self.label_tooltip = QLabel(self, Qt.ToolTip)
            self.timer_tooltip = QTimer(self)
            self.timer_tooltip.timeout.connect(self.label_tooltip.hide)
            self.timer_tooltip.setInterval(1000)

        # find nearest curve point
        nearest = (self._curves[0], _np.inf, None, None)
        for idx, curve in enumerate(self._curves):
            if not curve.isVisible():
                continue
            mappos = curve.mapFromScene(pos)
            posx, posy = mappos.x(), mappos.y()
            xData, yData = curve.curve.xData, curve.curve.yData
            if not xData.size:
                continue
            diffx = xData - posx
            idx = _np.argmin(_np.abs(diffx))
            if diffx[idx] < 0.5:
                valx, valy = xData[idx], yData[idx]
                diffy = abs(valy - posy)
                if diffy < nearest[1]:
                    nearest = (curve, diffy, valx, valy)

        # show tooltip
        curve, diffy, valx, valy = nearest
        ylimts = self.getViewBox().state['viewRange'][1]
        ydelta = ylimts[1] - ylimts[0]
        if diffy < 1e-2*ydelta:
            txt = Time(timestamp=valx).get_iso8601()+'\n'
            txt += f'{curve.name()}: {valy:.3f}'
            font = QApplication.instance().font()
            font.setPointSize(font.pointSize() - 10)
            palette = QPalette()
            palette.setColor(QPalette.WindowText, curve.color)
            palette.setColor(QPalette.Window, Qt.darkGray)
            self.label_tooltip.setText(txt)
            self.label_tooltip.setFont(font)
            self.label_tooltip.setPalette(palette)
            self.label_tooltip.move(self.mapToGlobal(pos.toPoint()))
            self.label_tooltip.show()
            self.timer_tooltip.start()
            curve.scatter.setData(
                pos=[(valx, valy), ], symbol='o', size=15,
                brush=mkBrush(curve.color))
            curve.scatter.show()
