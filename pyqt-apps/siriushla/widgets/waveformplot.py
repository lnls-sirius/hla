"""Waveform plot widget."""

from qtpy.QtCore import Slot

from pyqtgraph import ViewBox, AxisItem

from pydm.widgets import PyDMWaveformPlot


class SiriusWaveformPlot(PyDMWaveformPlot):
    """Sirius Waveform Plot widget."""

    def __init__(self, *args, **kwargs):
        """Init and change some configurations."""
        super().__init__(*args, **kwargs)
        new_axis = AxisItem(orientation='left')
        self.plotItem.setAxisItems({'left': new_axis})

        # show auto adjust button
        self.plotItem.showButtons()

        # use pan mouse mode (3-button)
        self.plotItem.getViewBox().setMouseMode(ViewBox.PanMode)

    @property
    def legend(self):
        """Legend object."""
        return self._legend

    @Slot()
    def redrawPlot(self):
        """
        Request a redraw from each curve in the plot.
        Called by curves when they get new data.
        """
        if not self._needs_redraw:
            return
        for curve in self._curves:
            if not (isinstance(curve.x_waveform, float) or isinstance(curve.y_waveform, float) or \
                    isinstance(curve.x_waveform, int) or isinstance(curve.y_waveform, int)):
                curve.redrawCurve()
        self._needs_redraw = False
