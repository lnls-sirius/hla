"""Define control widget for fast correctors."""
from .BaseMagnetControlWidget import BaseMagnetControlWidget


class SIFastCorrectorControlWidget(BaseMagnetControlWidget):
    """Storage ring fast correctors."""

    def _getPattern(self):
        return "SI-\w{3,4}:MA-(FCH|FCV)(-[1-2])*"

    def _getFilter(self):
        return {"sec": "SI", "sub": "\w{4}", "dev": "(FCH|FCV).*"}

    def _getStrength(self):
        return "Kick"

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _divideBySection(self):
        return True

    def _getGroups(self):
        return [('Horizontal Fast Correctors', '-FCH'),
                ('Vertical Fast Corretors', '-FCV')]
