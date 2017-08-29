"""This module defines a widget that represent a PV as bar graph."""
import logging

import epics
import numpy as np
import pyqtgraph as pg

from pydm.widgets.channel import PyDMChannel
from pydm.PyQt.QtCore import QTimer, QSize

logging.basicConfig(level=logging.DEBUG)


class BarGraphModel:
    """Model for BarGraphWidget."""

    def __init__(self, waveform=[], width=1, brush="b", scale=1):
        """Set waveform and parameters."""
        self._pvname = None

        self._waveform = waveform

        self._size = len(self._waveform)
        self.x = range(self.size)

        self.width = width
        self.brush = brush
        self.scale = scale

    @property
    def waveform(self):
        """Return the value read from PV."""
        return self._waveform

    @waveform.setter
    def waveform(self, waveform):
        self._waveform = waveform
        self.size = len(waveform)

    @property
    def size(self):
        """Return size of PV array."""
        return self._size

    @size.setter
    def size(self, size):
        self._size = size
        self.x = range(self._size)

    def connected(self):
        """Return always connected."""
        return True


class EpicsBarGraphModel:
    """Handle the model data to be represented as a bar graph."""

    TIMEOUT = 0.2

    def __init__(self, width=1, brush=None, scale=1, update_interval=1000):
        """Set model data.

        pvname - pv to be represented as a graph
        size - size of the array
        scale - scale the array values
        update_interval - interval to read PV and update view
        """
        self._pvname = None

        self._size = 0
        self.x = range(self.size)

        self.width = width
        self.brush = brush
        self.scale = scale
        self.update_interval = update_interval

        self._connect()

    @property
    def pvname(self):
        """Name of the PV to retrieve value."""
        return self._pvname

    @pvname.setter
    def pvname(self, pvname):
        self._pvname = pvname
        self._connect()

        self.x = range(self._size)

    @property
    def waveform(self):
        """Retrun the value read from PV."""
        waveform = self.pv.get(timeout=self.TIMEOUT)
        return [val*self.scale for val in waveform]

    @property
    def size(self):
        """Return size of PV array."""
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def connected(self):
        """Return connection status."""
        return self.pv.status

    def _connect(self):
        if self.pvname is not None:
            self.pv = epics.PV(self.pvname)
            self.pv.wait_for_connection(timeout=self.TIMEOUT)
            if self.pv is None:
                logging.warning("Failed to connect to PV.")
            else:
                self.pv.get(timeout=self.TIMEOUT)
                self.size = self.pv.count
        else:
            self.pv = None


class PyDMBarGraphModel:
    """Implement a data model for the bar graph widget based on PyDMChannel.

    init_channel - pv to be represented as a graph
    size - size of the array
    scale - scale the array values
    update_interval - interval to read PV and update view
    """

    def __init__(self, init_channel=None, width=1, brush=None,
                 scale=1, update_interval=1000):
        """Set epics channel connection."""
        self.channel = init_channel
        self._channels = None

        self._connected = False

        self._size = 0
        self.x = range(self.size)

        self.width = width
        self.brush = brush
        self.scale = scale
        self.update_interval = update_interval

        self._waveform = []

    @property
    def waveform(self):
        """Return waveform array."""
        waveform = self._waveform
        return np.array([val*self.scale for val in waveform])

    @waveform.setter
    def waveform(self, waveform):
        self._waveform = waveform

    @property
    def size(self):
        """Return size of PV array."""
        return self._size

    @size.setter
    def size(self, size):
        self._size = size
        self.x = range(self._size)

    @property
    def connected(self):
        """Return connection status."""
        return self._connected

    # @pyqtSlot(bool)
    def connectionChanged(self, conn):
        """Slot called when connection state changes."""
        logging.debug("Connection changed to {}".format(conn))
        self._connected = conn

    def valueChanged(self, value):
        """Slot called when value changes."""
        pass

    # @pyqtSlot(list)
    def waveformChanged(self, waveform):
        """Slot called when value changes (PV of type array)."""
        self.waveform = waveform

    # @pyqtSlot(int)
    def countChanged(self, count):
        """Slot called when count changes."""
        self.size = count

    def channels(self):
        """Define slots and signals mappings for the epics channel."""
        if self._channels is None:
            self._channels = [
                PyDMChannel(
                    address=self.channel,
                    connection_slot=lambda conn: self.connectionChanged(conn),
                    value_slot=lambda val: self.valueChanged(val),
                    waveform_slot=lambda wvfrm: self.waveformChanged(wvfrm),
                    count_slot=lambda count: self.countChanged(count))]
        return self._channels


class BaseBarGraphWidget(pg.PlotWidget):
    """Widget that represents a waveform as a bar graph.

    Uses pyqtgraph (PlotWidget and BarGraphItem) to represent a wave,
    usually an array, as a bar graph.

    Functions:
        set_scale - sets a scale factor for viewing the graph;
        set_width - set the widtg of the bars;
        set_brush - set brush color.
    """

    # Public Interface
    def set_scale(self, scale):
        """Set scale."""
        self.model.scale = scale

    def set_width(self, width):
        """Set bar width."""
        self.model.width = width

    def set_brush(self, color):
        """Set brush color."""
        self.model.brush = color

    # Private methods
    def _plot(self):
        y = self.model.waveform
        if y is None:
            logging.warning("Failed to read PV value")
            return

        if not self.model.connected:
            logging.warning("Connection is down")
            return

        item = pg.BarGraphItem(x=self.model.x, height=y,
                               width=self.model.width, brush=self.model.brush)
        self.addItem(item)
        self.plot()

    def _update(self):
        self.clear()
        self._plot()

    def sizeHint(self):
        """Preferred size."""
        return QSize(2048, 400)


class BarGraphWidget(BaseBarGraphWidget):
    """Widget to show a waveform as graph of bars.

    Functions:
        set_waveform - plot a waveform (array) as a bar graph;
        Also see BaseBarGraphWidget.
    """

    def __init__(self, **kwargs):
        """Init PlotWidget.

        Constructor optional parameters:
            - scale: scale factor;
            - width: bar width;
            - brush: brush color;
            - waveform: waveform to be displayed.
        """
        super().__init__()
        # self.model = BarGraphModel(**kwargs)
        self.model = BarGraphModel(**kwargs)

    # Public Interface
    def set_waveform(self, waveform):
        """Set waveform."""
        self.model.waveform = waveform
        self._update()


class PyDMBarGraph(BaseBarGraphWidget):
    """Widget that represents a PV as a bar graph.

    The widget reads a PV value and updates it synchronously.

    Functions:
        set_update_interval - set the update interval at which the PV value is
                              is queried and the view is updated;
        Also see BaseBarGraphWidget.
    """

    def __init__(self, channel=None, **kwargs):
        """Set model and start timer.

        Constructor parameters:
            - channel: pv channel to be read;
            - scale: scale factor;
            - width: bar width;
            - brush: brush color;
            - update_interval: interval to update view.
        """
        super().__init__()
        self.model = PyDMBarGraphModel(init_channel=channel, **kwargs)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update)
        self.update_timer.start(self.model.update_interval)

    # Public interface
    def set_update_interval(self, interval):
        """Set timer update interval."""
        self.update_timer.stop()
        self.model.update_interval = interval
        self.update_timer.start(self.model.update_interval)

    def channels(self):
        """Used by PYDmApplication to set the model channel."""
        if isinstance(self.model, PyDMBarGraphModel):
            return self.model.channels()
        return [PyDMChannel()]


if __name__ == "__main__":
    import sys
    from pydm import PyDMApplication

    app = PyDMApplication(None, sys.argv)
    w = BarGraphWidget()
    # w.model.pvname = "fac-lnls455-linux-SI-13C4:DI-DCCT:BbBCurrent-Mon"
    w.set_scale(100)
    w.set_brush("b")
    pv = "fac-lnls455-linux-SI-13C4:DI-DCCT:BbBCurrent-Mon"
    w.model.channel = "ca://" + pv
    w.show()
    sys.exit(app.exec_())
