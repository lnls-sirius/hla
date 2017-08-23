"""Define control widget for fast correctors."""
from .BaseMagnetControlWidget import BaseMagnetControlWidget


class SiFastCorrectorControlWidget(BaseMagnetControlWidget):
    """Storage ring fast correctors."""

    def _getPattern(self):
        return "SI-\w{3,4}:MA-(FCH|FCV)(-[1-2])*"

    def _getStrength(self):
        return "Kick"

    def _getHeader(self):
        return ["State", "Magnet", "Cur-SP", "Cur-Mon", "Kick-SP", "Kick-Mon"]

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _divideBySection(self):
        return True

    def _getGroups(self):
        return [('Horizontal Fast Correctors', '-FCH'),
                ('Vertical Fast Corretors', '-FCV')]
