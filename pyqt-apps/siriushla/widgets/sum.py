"""Sirius Sum Label."""
from epics import PV
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel


class SiriusSumLabel(QLabel):
    """
    A QLabel thar receives multiple PVs and presents the sum of their values.

    Parameters
    ----------
    parent: QWidget
        The parent widget for the Label
    channels: list, optional
        The channels to be used by the widget
    """

    def __init__(self, parent=None, channels=[]):
        super(QLabel, self).__init__(parent)
        self.setTextFormat(Qt.PlainText)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setText("######")
        self.sum_value = 0

        self.channels = {}
        for i, ch in enumerate(channels):
            self.channels[i] = PV(ch)
            self.channels[i].add_callback(self._handle_sum_update)

    def _handle_sum_update(self, value, **kwargs):
        """
        Whenever a channel's value is updated, updates the text to reflect
        the changing sum.
        """
        _ = kwargs
        if value:
            self.sum_value += value
            self.setText(str(self.sum_value))
