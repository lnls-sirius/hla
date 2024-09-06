"""Bar graph."""

from pyqtgraph import BarGraphItem, PlotWidget
from qtpy.QtCore import QTimer

from ...widgets import SiriusConnectionSignal as _ConnSignal


class BarGraph(PlotWidget):
    """Bar Graph."""

    def __init__(self, channels=list(), xLabels=list(), yLabel='', title=''):
        """Init."""
        super().__init__()
        self._channels = list()
        for chn in channels:
            self._channels.append(_ConnSignal(chn))
        self._xLabels = xLabels
        self._yLabel = yLabel

        self.showGrid(x=True, y=True)
        self.setBackground('w')
        self.setXRange(min=-0.5, max=len(xLabels)-0.5)
        self.setTitle(title)
        self.setLabel('left', text=self._yLabel)
        self.getAxis('left').setStyle(
            autoExpandTextSpace=False, tickTextWidth=30)
        self.getAxis('bottom').setTicks(
            [[(i, l) for i, l in enumerate(self._xLabels)]])

        self._baritems = dict()
        for idx, lbl in enumerate(self._xLabels):
            baritem = BarGraphItem(
                x=[idx, ], width=1, height=0, brush='b')
            self.addItem(baritem)
            self._baritems[idx] = baritem

        self._timer = QTimer()
        self._timer.timeout.connect(self._update_graph)
        self._timer.setInterval(500)  # ms
        self._timer.start()

    def _update_graph(self):
        wave = list()
        for idx, chn in enumerate(self._channels):
            value = chn.value if chn.value is not None else 0
            wave.append(value)
            self._baritems[idx].setOpts(height=value)
