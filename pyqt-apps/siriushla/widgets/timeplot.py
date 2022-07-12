import numpy as _np
import time

from qtpy.QtCore import Qt, Signal, Slot, QTimer, Property
from qtpy.QtGui import QPalette
from qtpy.QtWidgets import QInputDialog, QLabel, QApplication, QAction

from pyqtgraph import ViewBox, mkBrush

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
    def redrawCurve(self, min_x=None, max_x=None):
        """
        Rederive redrawCurve to use data only refered to timespan.
        """
        try:
            now = Time.now().timestamp()
            xmin = now - self.parent.timeSpan
            idcs = _np.where(self.data_buffer[0] >= xmin)[0]
            if idcs.size and idcs[0] != 0 and \
                    self.data_buffer[0, idcs[0]-1] != 0:
                idcs = _np.r_[idcs[0]-1, idcs]
            x = self.data_buffer[0, idcs].astype(_np.float)
            y = self.data_buffer[1, idcs].astype(_np.float)

            if not self._plot_by_timestamps:
                x -= now

            if self.plot_style is None or self.plot_style == 'Line':
                self.setData(y=y, x=x)
            elif self.plot_style == 'Bar':
                min_index = _np.searchsorted(x, min_x)
                max_index = _np.searchsorted(x, max_x) + 1
                self._setBarGraphItem(
                    x=x[min_index:max_index], y=y[min_index:max_index])
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

    def createCurveItem(self, y_channel, plot_by_timestamps, plot_style, name,
                        color, yAxisName, useArchiveData, **plot_opts):
        return SiriusTimePlotItem(
            self, y_channel, plot_by_timestamps=plot_by_timestamps,
            plot_style=plot_style, name=name, color=color,
            yAxisName=yAxisName, **plot_opts)

    def updateXAxis(self, update_immediately=False):
        """Reimplement to show only existing range."""
        if len(self._curves) == 0:
            return

        if self._plot_by_timestamps:
            if self._update_mode == PyDMTimePlot.OnValueChange:
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
