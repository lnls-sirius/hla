"""Widgets to control Trim Quadrupoles magnets."""
from .BaseMagnetControlWidget import BaseMagnetControlWidget


class TrimControlWidget(BaseMagnetControlWidget):
    """Class to control a Fam Quad from the Sirius section."""

    def _getPattern(self):
        return "SI-\d{2}\w\d:MA-Q[DF0-9].*"

    def _getStrength(self):
        return "KL"

    def _getHeader(self):
        return ["State", "Magnet", "Cur-SP", "Cur-Mon",
                "KL-SP", "KL-Mon"]

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _divideBySection(self):
        return False

    def _getGroups(self):
        return [('Trims (1-10)', "SI-(0\d|10)"),
                ('Trims (11-20)', "SI-(1[1-9]|20)")]
