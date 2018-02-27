"""Define widget for controlling slow correctors."""
from .BaseMagnetControlWidget import BaseMagnetControlWidget


class SISlowCorrectorControlWidget(BaseMagnetControlWidget):
    """Storage ring slow correctors."""

    def _getPattern(self):
        return "SI-\w{4}:MA-(CH|CV)(-[1-2])*"

    def _getFilter(self):
        return {"sec": "SI", "sub": "\w{4}", "dev": "(CH|CV).*"}

    def _getStrength(self):
        return "Kick"

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _divideBySection(self):
        return True

    def _getGroups(self):
        return [('Horizontal Slow Correctors', '-CH'),
                ('Vertical Slow Corretors', '-CV')]


class BoSlowCorrectorControlWidget(SISlowCorrectorControlWidget):
    """Booster slow corretors."""

    def _getPattern(self):
        return "BO-\w{3}:MA-(CH|CV)(-[1-2])*"

    def _getFilter(self):
        return {"sec": "BO", "sub": "\w{3}", "dev": "(CH|CV).*"}

    def _divideBySection(self):
        return False


class TBSlowCorrectorControlWidget(SISlowCorrectorControlWidget):
    """To booster transport line slow corrector."""

    def _getPattern(self):
        return "TB-\d{2}:MA-(CH|CV).*"

    def _getFilter(self):
        return {"sec": "TB", "sub": "\d{2}", "dev": "(CH|CV).*"}

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return True


class TSSlowCorrectorControlWidget(SISlowCorrectorControlWidget):
    """To sirius transport line slow correctors."""

    def _getPattern(self):
        return "TS-\w{2}:MA-(CH|CV)(-[1-2])*"

    def _getFilter(self):
        return {"sec": "TS", "sub": "\w{2}", "dev": "(CH|CV).*"}

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return True
