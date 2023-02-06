"""Waveform plot widget."""

from pyqtgraph import ViewBox

from pydm.widgets import PyDMWaveformPlot


class SiriusWaveformPlot(PyDMWaveformPlot):
    """Sirius Waveform Plot widget."""

    def __init__(self, *args, **kwargs):
        """Init and change some configurations."""
        super().__init__(*args, **kwargs)

        # show auto adjust button
        self.plotItem.showButtons()

        # use pan mouse mode (3-button)
        self.plotItem.getViewBox().setMouseMode(ViewBox.PanMode)

    @property
    def legend(self):
        """Legend object."""
        return self._legend
