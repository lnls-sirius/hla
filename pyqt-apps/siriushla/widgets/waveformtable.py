"""Sirius Waveform Table Widget."""

import numpy as _np

from pydm.widgets import PyDMWaveformTable


class SiriusWaveformTable(PyDMWaveformTable):
    """Handle bugs for None, float and int values."""

    def value_changed(self, new_waveform):
        """
        Callback invoked when the Channel value is changed.

        Parameters
        ----------
        new_waveform : np.ndarray
            The new waveform value from the channel.
        """
        if new_waveform is None:
            return
        elif isinstance(new_waveform, (float, int)):
            new_waveform = _np.array([new_waveform])
        super().value_changed(new_waveform)
