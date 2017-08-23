"""Sked Quadrupole control widgets."""
from .BaseMagnetControlWidget import BaseMagnetControlWidget


class SiSkewQuadControlWidget(BaseMagnetControlWidget):
    """Storage ring skew quads."""

    def _getPattern(self):
        return "SI-\w{4}:MA-QS"

    def _getStrength(self):
        return "KL"

    def _getHeader(self):
        return ["State", "Magnet", "Cur-SP", "Cur-Mon", "KL-SP", "KL-Mon"]

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _divideBySection(self):
        return True

    def _getGroups(self):
        return [('Skew Quad (01 - 10)', '(0\d|10)'),
                ('Skew Quad (11 - 20)', '(1[1-9]|20)')]


class BoSkewQuadControlWidget(SiSkewQuadControlWidget):
    """Booster skew quads."""

    def _getPattern(self):
        return "BO-\w{3}:MA-QS"

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return False

    def _getGroups(self):
        return [('Skew Quad', '')]
