"""PyDMScrollBar module."""

from qtpy.QtCore import Qt, Signal
from .QDoubleScrollBar import QDoubleScrollBar
from pydm.widgets.base import PyDMWritableWidget, TextFormatter


class PyDMScrollBar(QDoubleScrollBar, TextFormatter, PyDMWritableWidget):
    """
    A QDoubleScrollBar with support for Channels and more from PyDM.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the scroll bar
    init_channel : str, optional
        The channel to be used by the widget.
    orientation : Qt.Horizontal, Qt.Vertical
        Orientation of the scroll bar
    precision : int
        Precision to be use. Used to calculate size of the scroll bar step

    """

    value_changed_signal = Signal([int], [float], [str])
    connected_signal = Signal()
    disconnected_signal = Signal()

    def __init__(self, parent=None, orientation=Qt.Horizontal,
                 init_channel=None):
        """Init."""
        QDoubleScrollBar.__init__(self, orientation, parent)
        PyDMWritableWidget.__init__(self, init_channel)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setInvertedControls(False)

        self.setTracking(True)
        self.actionTriggered.connect(self.send_value)

    def widget_ctx_menu(self):
        """Return context menu."""
        return self.contextMenu

    def send_value(self):
        """Emit a :attr:`send_value_signal` to update channel value."""
        value = self.sliderPosition
        if self._connected and self.channeltype is not None:
            self.send_value_signal[self.channeltype].emit(
                self.channeltype(value))

    def ctrl_limit_changed(self, which, new_limit):
        """Set new upper/lower limits as maximum/minimum values."""
        PyDMWritableWidget.ctrl_limit_changed(self, which, new_limit)

        if which == "UPPER":
            self.setMaximum(self._upper_ctrl_limit)
        else:
            self.setMinimum(self._lower_ctrl_limit)

    def precision_changed(self, new_precision):
        """Set the step size based on the new precision value received."""
        TextFormatter.precision_changed(self, new_precision)
        self.setDecimals(round(self._prec))
        self.setSingleStep(1/10**self._prec)
        self.setPageStep(10/10**self._prec)
