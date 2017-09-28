"""Define widget for controlling slow correctors."""
from .BaseMagnetControlWidget import BaseMagnetControlWidget


class SiSlowCorrectorControlWidget(BaseMagnetControlWidget):
    """Storage ring slow correctors."""

    def _getPattern(self):
        return "SI-\w{4}:MA-(CH|CV)(-[1-2])*"

    def _getFilter(self):
        return {"section": "SI", "subsection": "\w{4}", "device": "(CH|CV).*"}

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
        return [('Horizontal Slow Correctors', '-CH'),
                ('Vertical Slow Corretors', '-CV')]


class BoSlowCorrectorControlWidget(SiSlowCorrectorControlWidget):
    """Booster slow corretors."""

    def _getPattern(self):
        return "BO-\w{3}:MA-(CH|CV)(-[1-2])*"

    def _getFilter(self):
        return {"section": "BO", "subsection": "\w{3}", "device": "(CH|CV).*"}

    def _divideBySection(self):
        return False


class TBSlowCorrectorControlWidget(SiSlowCorrectorControlWidget):
    """To booster transport line slow corrector."""

    def _getPattern(self):
        return "TB-\d{2}:MA-(CH|CV).*"

    def _getFilter(self):
        return {"section": "TB", "subsection": "\d{2}", "device": "(CH|CV).*"}

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return True


class TSSlowCorrectorControlWidget(SiSlowCorrectorControlWidget):
    """To sirius transport line slow correctors."""

    def _getPattern(self):
        return "TS-\w{2}:MA-(CH|CV)(-[1-2])*"

    def _getFilter(self):
        return {"section": "TS", "subsection": "\w{2}", "device": "(CH|CV).*"}

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return True
