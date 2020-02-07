"""Define widget for controlling slow correctors."""
from .BasePSControlWidget import BasePSControlWidget


class LISolenoidControlWidget(BasePSControlWidget):
    """Storage ring slow correctors."""

    def _getFilter(self, subsection=None):
        return {"sec": "LI", "dev": "Slnd.*"}

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Solenoid', '')]
