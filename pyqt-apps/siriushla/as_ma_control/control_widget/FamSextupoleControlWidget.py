"""Define control widget for family sextupoles."""
from .BaseMagnetControlWidget import BaseMagnetControlWidget


class SiFamSextupoleControlWidget(BaseMagnetControlWidget):
    """Storage ring sextupoles."""

    def _getPattern(self):
        return "SI-Fam:MA-S(\w+[0-9]*|[0-9])"

    def _getFilter(self):
        return {"section": "SI", "subsection": "Fam", "device": "S[DF].*"}

    def _getStrength(self):
        return "SL"

    def _getHeader(self):
        return ["State", "Magnet", "Cur-SP", "Cur-Mon", "SL-SP", "SL-Mon"]

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _divideBySection(self):
        return False

    def _getGroups(self):
        return [('Focusing Sextupoles', '-SF'),
                ('Defocusing Sextupoles', '-SD')]


class BoFamSextupoleControlWidget(SiFamSextupoleControlWidget):
    """Booster sextupoles."""

    def _getPattern(self):
        return "BO-Fam:MA-S(\w+[0-9]*|[0-9])"

    def _getFilter(self):
        return {"section": "BO", "subsection": "Fam", "device": "S[DF].*"}

    def _hasScrollArea(self):
        return False
