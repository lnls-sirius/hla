"""Sirius Enum ComboBox."""

from qtpy.QtCore import Qt
from pydm.widgets import PyDMEnumComboBox


class SiriusEnumComboBox(PyDMEnumComboBox):
    """Subclass PyDMEnumComboBox to reimplement whellEvent."""

    def __init__(self, parent, init_channel=None):
        """Initialize object."""
        super().__init__(parent=parent, init_channel=init_channel)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        """Reimplement wheel event to ignore event when out of focus."""
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)
